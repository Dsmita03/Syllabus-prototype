import os
import requests
import json
import re
import time
from typing import List, Dict, Any,Tuple
from dotenv import load_dotenv

# --- AI and PDF Processing Imports ---
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Configuration for Groq API ---
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# Using a fast and capable Llama3 model available on Groq
GROQ_MODEL_NAME = "llama-3.1-8b-instant"
# DPI for rendering PDF pages to images for OCR
OCR_DPI = 300
# Character limit for text chunks sent to the API.
# This value is chosen conservatively to leave room for the large system prompt.
TEXT_CHUNK_SIZE = 4000


class SyllabusProcessor:
      def __init__(self):
        """
        Initializes the processor, loading the Groq API key from environment variables.
        """
        # For Google Colab, it's better to use the userdata library
        try:
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                 # Fallback for local dev if Colab-specific method fails
                 
                 self.api_key = os.getenv("GROQ_API_KEY")
            print("Loaded GROQ_API_KEY from Colab Secrets.")
        except (ImportError, KeyError):
            self.api_key = os.getenv("GROQ_API_KEY")
            if self.api_key:
                print("Loaded GROQ_API_KEY from .env file.")
            else:
                 raise ValueError("GROQ_API_KEY not found. Please set it in Colab Secrets or a .env file.")

        print("SyllabusProcessor initialized with Groq API.")


    # PART I: ROBUST PDF & TEXT EXTRACTION

      def _extract_text_with_table_detection(self, doc: fitz.Document) -> Tuple[str, bool]:
          """
          Specialized method for PDFs with clear table structures.
          """
          full_text = ""
          table_char_count = 0
          for page in doc:
             table_list = page.find_tables().tables
             if table_list:
                print(f"Found {len(table_list)} table(s) on page {page.number + 1}.")
                for table in table_list:
                    extracted_table = table.extract()
                    if extracted_table:
                       for row in extracted_table:
                           row_text = " | ".join(str(cell).replace('\n', ' ') if cell is not None else "" for cell in row)
                           full_text += row_text + "\n"
                           table_char_count += len(row_text)
          is_successful = table_char_count > 500
          return full_text, is_successful

      def _extract_text_with_block_detection(self, doc: fitz.Document) -> Tuple[str, bool]:
        """
        General purpose method for unstructured or semi-structured PDFs.
        """
        full_text = ""
        for page in doc:
            blocks = page.get_text("blocks", sort=True)
            for b in blocks:
                full_text += b[4]
        is_successful = len(full_text.strip()) > 200
        return full_text, is_successful

      def _ocr_scanned_pdf(self, pdf_path: str) -> Tuple[str, bool]:
        """
        Performs OCR on a scanned PDF using Tesseract after pre-processing images.
        """
        try:
            images = convert_from_path(pdf_path, dpi=OCR_DPI)
            full_text = ""
            print(f"Converted PDF to {len(images)} image(s) for OCR.")
            for i, img in enumerate(images):
                print(f"Processing page {i+1} with OCR...")
                open_cv_image = np.array(img)
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                text = pytesseract.image_to_string(thresh, lang='eng')
                full_text += text + f"\n\n--- Page {i+1} End ---\n\n"
            is_successful = len(full_text.strip()) > 0
            print(f"OCR extraction yielded {len(full_text.strip())} characters.")
            return full_text, is_successful
        except Exception as e:
            print(f"Error processing {pdf_path} with OCR: {e}")
            return "", False

      def _get_text_from_pdf(self, pdf_path: str) -> str:
        """
        Hybrid pipeline controller. Tries block, then table, then OCR extraction.
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise Exception(f"Error opening {pdf_path} with PyMuPDF: {e}")
        print("Step 1: Attempting general block extraction...")
        text, success = self._extract_text_with_block_detection(doc)
        if success:
            print("General block extraction successful.")
            doc.close()
            return text
        print("Block extraction not suitable. Falling back to table extraction...")
        text, success = self._extract_text_with_table_detection(doc)
        if success:
            print("Table extraction successful. Using this method.")
            doc.close()
            return text
        doc.close()
        print("Digital extraction yielded poor results. Falling back to OCR...")
        text, success = self._ocr_scanned_pdf(pdf_path)
        if success:
            print("Successfully extracted text using OCR.")
            return text
        else:
            raise Exception(f"Critical Error: Could not extract text from {pdf_path} using any method.")

      def _extract_text_from_txt(self, file_path: str) -> str:
        """Extracts text from a plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {e}")

    # PART II: AI-POWERED MODULE EXTRACTION (ADVANCED PROMPT & RESILIENT)

      def _extract_modules_with_llm(self, syllabus_text: str) -> List[Dict[str, Any]]:
        """
        Sends a CHUNK of syllabus text to the Groq API to extract modules.
        This version includes a retry mechanism with exponential backoff to handle rate limits.
        """
        # The system prompt remains unchanged as it is highly effective.
        system_prompt = """
You are an expert academic data extraction system.
Your task is to extract structured academic content (modules, units, topics)
from diverse syllabus texts into a JSON format.

**Instructions:**
1.  **Exhaustive Processing**: You MUST process the ENTIRE syllabus text from beginning to end and identify ALL distinct modules, topics, or units. Do not stop after finding the first one.
2.  **Segmentation and Logic**:
    * For each module, create a concise `module_title`. The text that follows the heading is the `description`. **Crucially, do not include the description text inside the title.**
    * If a large text block contains an internal numbered or bulleted list (like in Example 12), you MUST split each item in that list into its own separate module.
3.  **Schema and Fields**:
    * Use the appropriate schema ('Module/Unit' style or 'Topic/Sub-topics' style).
    * Return ONLY the fields genuinely present in the text. Use `null` for unavailable fields.
4.  **Output Format**: Your entire output must be a single, valid JSON object.
5.  **Boundary Detection and Metadata Handling**: Your primary task is to extract the core list of academic modules/units. You MUST actively ignore all surrounding metadata. This includes, but is not limited to:
    * **Preamble**: Course Objectives, Course Learning Rationale (CLR), Program Outcomes (PO), Prerequisites, Course Code, Credits.
    * **Postamble**: Course Outcomes (COs), Textbooks, Reference Books, Evaluation Schemes, Grading Policies.
    * **CRITICAL RULE**: Begin the extraction process ONLY from the line containing a heading like "Course Contents", "Syllabus", "Detailed Syllabus", or the very first "Unit I" / "Module 1". DISCARD ALL TEXT that comes before this starting point. Similarly, stop the extraction immediately when you encounter a heading like "Course Outcomes", "Textbooks", or "Reference books".

**Schemas:**
Case A - Module/Unit style:
{
  "modules": [
    {"module_number": "string or null","module_title": "string","description": "string","learning_outcome": "string or null"}
  ]
}
Case B - Topic/Sub-topics style (Use for table formats with these specific column headers):
{
  "modules": [
    { "Topic": "string", "Sub-topics": "string" }
  ]
}

---
**Example 1 (Unstructured Topic Format with Lecture Hours):**
Text: '''
Syllabus:
Introduction to Graph Theory [4L]
Definitions and Examples, Subgraphs, Complement of a graph, Graph Isomorphism.
Path, Cycles, Coloring [8L]
Walk, Trail, Path, Cycle, Euler Trails and Circuits, Planar Graphs.
'''
JSON Output:
{
  "modules": [
    {"module_number": null,"module_title": "Introduction to Graph Theory","description": "Definitions and Examples, Subgraphs, Complement of a graph, Graph Isomorphism." },
    {"module_number": null,"module_title": "Path, Cycles, Coloring","description": "Walk, Trail, Path, Cycle, Euler Trails and Circuits, Planar Graphs."}
  ]
}
---
**Example 2 (Table Format):**
Text: '''
10. Details of the Course:
Sl.No.  Contents
1.      CPU structure and functions, processor organization, ALU, data paths.
2.      Processor control, micro-operations, instruction fetch, hardwired control.
'''
JSON Output:
{
  "modules": [
    {"module_number": "1","module_title": "CPU structure and functions","description": "CPU structure and functions, processor organization, ALU, data paths."},
    {"module_number": "2","module_title": "Processor control","description": "Processor control, micro-operations, instruction fetch, hardwired control."}
  ]
}
---
**Example 3 (Numbered List Syllabus):**
Text: '''
Syllabus:
1. Information, Data, Data Types, Abstract Data Type (ADT), Data Structure.
2. Array as an ADT, Single and Multidimensional Arrays, Structures, Sparse Matrix.
3. Pointers, ADT Linked List, Singly Linked List, Doubly Linked List.
'''
JSON Output:
{
  "modules": [
    {"module_number": "1","module_title": "Information, Data, Data Types, ADT","description": "Information, Data, Data Types, Abstract Data Type (ADT), Data Structure."},
    {"module_number": "2","module_title": "Array as an ADT","description": "Array as an ADT, Single and Multidimensional Arrays, Structures, Sparse Matrix."},
    {"module_number": "3","module_title": "Pointers and Linked Lists","description": "Pointers, ADT Linked List, Singly Linked List, Doubly Linked List."}
  ]
}
---
**Example 4 (Unit/Numbered List):**
Text: '''
UNIT-I
1. Introduction to anatomy, anatomical terms, planes, organization of human body.
2. Musculo-skeletal system: Types of bones, structure & divisions of the skeleton system.
UNIT-II
1. Anatomy of Circulatory system: General plan of circulatory system and its components.
'''
JSON Output:
{
  "modules": [
    {"module_number": "I.1","module_title": "UNIT-I: Introduction to anatomy","description": "Introduction to anatomy, anatomical terms, planes, organization of human body."},
    {"module_number": "I.2","module_title": "UNIT-I: Musculo-skeletal system","description": "Musculo-skeletal system: Types of bones, structure & divisions of the skeleton system."},
    {"module_number": "II.1","module_title": "UNIT-II: Anatomy of Circulatory system","description": "Anatomy of Circulatory system: General plan of circulatory system and its components."}
  ]
}
---
**Example 5 (Module with Hours Format):**
Text: '''
Module:1 Ordinary Differential Equations (ODE) 6 hours
Second order non- homogenous differential equations with constant coefficients.
Module:2 Partial Differential Equations (PDE) 5 hours
Formation of partial differential equations - Singular integrals.
'''
JSON Output:
{
  "modules": [
    {"module_number": "1","module_title": "Ordinary Differential Equations (ODE)","description": "Second order non- homogenous differential equations with constant coefficients."},
    {"module_number": "2","module_title": "Partial Differential Equations (PDE)","description": "Formation of partial differential equations - Singular integrals."}
  ]
}
---
**Example 6 (Simple Topic List):**
Text: '''
The students will be exposed to the following topics:
Regular Expression Tools (e.g Awk)
Lex and Yacc
Bash Scripting
'''
JSON Output:
{
  "modules": [
    {"module_number": null,"module_title": "Regular Expression Tools (e.g Awk)","description": "Regular Expression Tools (e.g Awk)"},
    {"module_number": null,"module_title": "Lex and Yacc","description": "Lex and Yacc"},
    {"module_number": null,"module_title": "Bash Scripting","description": "Bash Scripting"}
  ]
}
---
**Example 7 (Long Unstructured Topic List):**
Text: '''
Thermodynamics: C, and C,: definition and relation; adiabatic changes; reversible and irreversible processes.
Second law thermodynamics; Joule Thomson and throttling processes; inversion temperature.
...
Industrial Chemistry: Solid, liquid and gaseous fuels; constituents of coal, carbonization of coal.
Electrochemistry: Conductance of electrolytic solutions, specific conductance.
'''
JSON Output:
{
  "modules": [
    {"module_number": null,"module_title": "Thermodynamics","description": "C, and C,: definition and relation; adiabatic changes; reversible and irreversible processes."},
    {"module_number": null,"module_title": "Second law thermodynamics","description": "Joule Thomson and throttling processes; inversion temperature."},
    {"module_number": null,"module_title": "Industrial Chemistry","description": "Solid, liquid and gaseous fuels; constituents of coal, carbonization of coal."},
    {"module_number": null,"module_title": "Electrochemistry","description": "Conductance of electrolytic solutions, specific conductance."}
  ]
}
---
**Example 8 (Highly Structured Table Format):**
Text: '''
"Unit No.","Topics to be Covered","Lecture Hours","Learning Outcome"
"1","Introduction: Need of compilers; Cousins of compilers; Compiler writing tools, compiler phases.","2","The students will be introduced with the language translator, their need and various phases of a compiler."
"2","Lexical analysis: Tokens, regular expressions, transition diagrams, Design of lexical analyzer generator.","5","Students will be familiar with various elements of a scanner (lexical analyzer). They will also learn how to use transition diagram or finite automata for designing a new lexical analyzer"
'''
JSON Output:
{
  "modules": [
    {"module_number": "1","topics_covered": "Introduction: Need of compilers; Cousins of compilers; Compiler writing tools, compiler phases.","lecture_hours": 2,"learning_outcome": "The students will be introduced with the language translator, their need and various phases of a compiler."},
    {"module_number": "2","topics_covered": "Lexical analysis: Tokens, regular expressions, transition diagrams, Design of lexical analyzer generator.","lecture_hours": 5,"learning_outcome": "Students will be familiar with various elements of a scanner (lexical analyzer). They will also learn how to use transition diagram or finite automata for designing a new lexical analyzer"}
  ]
}
---
**Example 9 (Paragraph Block Format):**
Text: '''
SECTION-1
Introduction: Introduction to web technology, Internet and WWW, web site planning and design issues, HTML5: structure of html document, commenting, formatting tags, list tags, hyperlink tags, image, table tags, frame tags, form tags, CSS, Bootstrap, JSON(6Hrs)
Client Side Technologies: JavaScript: Overview of JavaScript, Data types, Control Structures, Arrays, Functions and Scopes, Objects in JS, Form validation, DOM: Introduction, DOMlevels, DOM Objects, their properties and methods, Manipulating DOM (6 Mrs)
JQuery: Introduction, Loading JQuery, selecting elements, changing styles, creating elements, appending elements, removing elements, handling events. (2 Hrs)
'''
JSON Output:
{
  "modules": [
    {"module_number": null,"module_title": "Introduction","description": "Introduction to web technology, Internet and WWW, web site planning and design issues, HTML5: structure of html document, commenting, formatting tags, list tags, hyperlink tags, image, table tags, frame tags, form tags, CSS, Bootstrap, JSON(6Hrs)"},
    {"module_number": null,"module_title": "Client Side Technologies","description": "JavaScript: Overview of JavaScript, Data types, Control Structures, Arrays, Functions and Scopes, Objects in JS, Form validation, DOM: Introduction, DOMlevels, DOM Objects, their properties and methods, Manipulating DOM (6 Mrs)"},
    {"module_number": null,"module_title": "JQuery","description": "Introduction, Loading JQuery, selecting elements, changing styles, creating elements, appending elements, removing elements, handling events. (2 Hrs)"}
  ]
}
---
**Example 10 (Table Format with Topic/Sub-topics):**
Text: '''
"Module number" | "Topic" | "Sub-topics" | "Corresponding Lab Assignment"
"1" | "1. Rectifiers, Filters and Regulators:" | "Introduction to full-wave and half-wave rectifiers..." | "1. Simulation of full-wave..."
'''
JSON Output:
{
  "modules": [
    {"Topic": "Rectifiers, Filters and Regulators","Sub-topics": "Introduction to full-wave and half-wave rectifiers. Capacitor filter. Inductor filter, LC and π-section filter. Series and Shunt voltage regulator, percentage regulation. Regulator ICs 78xx and 79xx series. Introduction to SMPS."}
  ]
}
---
**Example 11 (Unstructured Paragraph to Logically Grouped Modules):**
Text: '''
Introduction, software life-cycle models, software requirements specification,
formal requirements specification and verification - axiomatic and algebraic
specifications, function-oriented software design, object-oriented design, UML,
design patterns, user interface design, coding and unit testing, integration
and systems testing, debugging techniques, software quality - SEI CMM and ISO-
9001. software reliability and fault-tolerance, software project planning,
monitoring, and control, software maintenance, computer-aided software
engineering (CASE), software reuse, component-based software development,
extreme programming.
'''
JSON Output:
{
  "modules": [
    { "module_number": null, "module_title": "Introduction and Life-cycle Models", "description": "Introduction; software life-cycle models (waterfall, incremental, evolutionary, spiral) and their trade-offs in planning and risk control." },
    { "module_number": null, "module_title": "Requirements and Formal Specification", "description": "Software requirements specification (SRS): functional and non-functional requirements, interfaces, structure; formal requirements specification and verification using axiomatic and algebraic methods." },
    { "module_number": null, "module_title": "Design Approaches and UML", "description": "Function-oriented software design; object-oriented design; UML diagrams for analysis and design; design patterns for recurring design problems; principles of cohesion, coupling, and modularity." },
    { "module_number": null, "module_title": "User Interface Design", "description": "UI design principles, analysis, prototyping, and evaluation; integrating usability into the software architecture and development process." },
    { "module_number": null, "module_title": "Coding, Unit, Integration and System Testing", "description": "Coding standards and practices; unit testing with stubs/mocks; integration strategies; system and validation testing; debugging techniques and defect lifecycle." },
    { "module_number": null, "module_title": "Software Quality and Process Standards", "description": "Software quality concepts, product vs. process quality; SEI CMM/CMMI levels and assessments; ISO 9001 quality management principles and compliance." },
    { "module_number": null, "module_title": "Reliability and Fault Tolerance", "description": "Software reliability fundamentals, models, and measurement; fault-tolerance techniques including error detection, recovery, and redundancy." },
    { "module_number": null, "module_title": "Project Planning, Monitoring, and Control", "description": "Estimation, scheduling, staffing, and resource planning; progress monitoring, metrics, status reporting, and risk management practices." },
    { "module_number": null, "module_title": "Maintenance and Evolution", "description": "Maintenance categories (corrective, adaptive, perfective, preventive); processes, cost drivers, refactoring, and technical debt management." },
    { "module_number": null, "module_title": "CASE, Reuse, Components, and XP", "description": "Computer-aided software engineering (CASE) tools across lifecycle; software reuse strategies; component-based software development; Extreme Programming (XP) values and practices." }
  ]
}
---
**Example 12 (Numbered List Inside a Single Text Block):**
Text: '''
Course Title: Basic Engineering
Topics Covered:
1.  Fundamentals of Circuits: Ohm's law, Kirchhoff's laws. (4 hours)
2.  Basics of Mechanics: Newton's laws of motion, friction. (5 hours)
3.  Introduction to Programming: Variables, loops, and functions in Python. (6 hours)
'''
JSON Output:
{
  "modules": [
    { "module_number": "1", "module_title": "Fundamentals of Circuits", "description": "Fundamentals of Circuits: Ohm's law, Kirchhoff's laws. (4 hours)" },
    { "module_number": "2", "module_title": "Basics of Mechanics", "description": "Basics of Mechanics: Newton's laws of motion, friction. (5 hours)" },
    { "module_number": "3", "module_title": "Introduction to Programming", "description": "Introduction to Programming: Variables, loops, and functions in Python. (6 hours)" }
  ]
}
---
**Example 13 (Content Boundary Detection):**
Text: '''
Course Objectives: To learn about programming.
Course Contents:
Unit I
Introduction to Python: Variables, data types, and basic syntax.
Unit II
Control Flow: If statements, for loops, while loops.
Course Outcome: Students will be able to write simple programs.
Textbooks:
1. Learning Python by Mark Lutz.
'''
JSON Output:
{
  "modules": [
    {"module_number": "I","module_title": "Introduction to Python","description": "Variables, data types, and basic syntax."},
    {"module_number": "II","module_title": "Control Flow","description": "If statements, for loops, while loops."}
  ]
}
---
**Example 14 (Complex Unit Heading Format - NEW & CRITICAL):**
Text: '''
Unit-1-Introduction to Microwaves and Sources 9 Hour
History of Microwave Engineering, Microwave transmission and Applications, Microwave Tubes, Klystron amplifier, Reflex Klystron oscillators, Magnetron oscillators, IMPATT, TRAPATT, Tunnel diode, Gunn diode.
Unit-3-Microwave Measurements 9 Hour
mpedance and Power measurement, Measurement of Frequency, Attenuation, Scattering parameters, Vector Network Analyzer, Signal Analyzer and Spectrum Analyzer Case study on VSWR and Impedance measurement
'''
JSON Output:
{
  "modules": [
    {"module_number": "1","module_title": "Introduction to Microwaves and Sources","description": "History of Microwave Engineering, Microwave transmission and Applications, Microwave Tubes, Klystron amplifier, Reflex Klystron oscillators, Magnetron oscillators, IMPATT, TRAPATT, Tunnel diode, Gunn diode."},
    {"module_number": "3","module_title": "Microwave Measurements","description": "mpedance and Power measurement, Measurement of Frequency, Attenuation, Scattering parameters, Vector Network Analyzer, Signal Analyzer and Spectrum Analyzer Case study on VSWR and Impedance measurement"}
  ]
}
"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": GROQ_MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the syllabus text to process:\n\n---\n\n{syllabus_text}"}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        max_retries = 5
        base_delay = 1  # start with a 1-second delay

        for attempt in range(max_retries):
            try:
                response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=300)
                
                if response.status_code == 429:
                    response.raise_for_status() 

                response.raise_for_status()
                
                response_data = response.json()
                json_output_str = response_data['choices'][0]['message']['content']
                extracted_data = json.loads(json_output_str)
                
                return extracted_data.get("modules", [])

            except requests.exceptions.RequestException as e:
                if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        raise Exception(f"API rate limit exceeded after {max_retries} attempts. Please wait and try again later.")
                else:
                    raise Exception(f"API request to Groq failed: {e}")
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Failed to parse JSON from Groq response: {e}")
                print(f"Raw response from model: {response.text}")
                raise Exception("The AI model returned an invalid or unexpected format.")
        
        return []

    # PART III: MAIN PROCESSING WORKFLOW (MODIFIED FOR ROBUSTNESS)

      def _clean_and_trim_text(self, text: str) -> str:
        """
        Removes preamble and postamble from syllabus text based on keywords.
        This is a crucial step to reduce payload size and improve AI focus.
        """
        start_keywords = [
            "Detailed Syllabus", "Syllabus", "Course Contents",
            "Course Content", "Unit I", "Module 1"
        ]
        end_keywords = [
            "Course Outcome", "Text book and Reference books", "Text Book",
            "Reference books", "Textbook", "Evaluation Scheme"
        ]

        start_pattern = "|".join(map(re.escape, start_keywords))
        end_pattern = "|".join(map(re.escape, end_keywords))

        start_match = re.search(start_pattern, text, re.IGNORECASE)
        if start_match:
            text = text[start_match.start():]

        end_match = re.search(end_pattern, text, re.IGNORECASE)
        if end_match:
            text = text[:end_match.start()]

        return text.strip()


      def _split_text_into_chunks(self, text: str) -> List[str]:
          """
          Splits text into chunks of a specified size without breaking words.
          """
          if len(text) <= TEXT_CHUNK_SIZE:
              return [text]

          chunks = []
          while text:
              if len(text) <= TEXT_CHUNK_SIZE:
                  chunks.append(text)
                  break
              split_pos = text.rfind('\n', 0, TEXT_CHUNK_SIZE)
              if split_pos == -1:
                  split_pos = text.rfind(' ', 0, TEXT_CHUNK_SIZE)

              if split_pos == -1:
                  split_pos = TEXT_CHUNK_SIZE

              chunks.append(text[:split_pos])
              text = text[split_pos:].lstrip()
          return chunks


      def process_syllabus(self, file_path: str) -> Dict[str, Any]:
        """
        Executes the full, AI-powered pipeline from file to structured module data.
        Now includes pre-processing and chunking for robustness.
        """
        try:
            print(f"Starting AI-powered syllabus processing: {os.path.basename(file_path)}")

            print("Extracting text from file...")
            if file_path.lower().endswith(".pdf"):
                full_text = self._get_text_from_pdf(file_path)
            elif file_path.lower().endswith(".txt"):
                full_text = self._extract_text_from_txt(file_path)
            else:
                raise Exception("Unsupported file format.")

            if not full_text or not full_text.strip():
                raise Exception("No readable text found in the uploaded file")

            print(f"Text extraction successful: {len(full_text):,} characters extracted")

            print("Pre-processing text to remove irrelevant sections...")
            cleaned_text = self._clean_and_trim_text(full_text)
            print(f"Text cleaned. New length: {len(cleaned_text):,} characters.")

            if not cleaned_text:
                raise Exception("No relevant syllabus content found after cleaning.")

            text_chunks = self._split_text_into_chunks(cleaned_text)
            print(f"Text split into {len(text_chunks)} chunk(s) for processing.")

            all_modules = []
            for i, chunk in enumerate(text_chunks):
                print(f"\nAnalyzing chunk {i+1}/{len(text_chunks)} with AI...")
                modules_from_chunk = self._extract_modules_with_llm(chunk)
                if modules_from_chunk:
                    all_modules.extend(modules_from_chunk)
                    print(f"AI extracted {len(modules_from_chunk)} modules from this chunk.")

            if not all_modules:
                raise Exception("AI could not identify any modules from the text.")

            print(f"\nAI successfully created a total of {len(all_modules)} learning modules.")

            formatted_modules = []
            for i, mod in enumerate(all_modules):
                if "Topic" in mod:
                   title = mod.get("Topic", "Untitled Topic")
                   content = mod.get("Sub-topics", "No sub-topics available.")
                else:
                   title = mod.get("module_title", "Untitled Module")
                   content = mod.get("description") or "No description available."

                formatted_modules.append({
                    "id": f"module_{i + 1}",
                    "title": title,
                    "content": content
                })

            return {
                "success": True,
                "original_text_length": len(full_text),
                "modules": formatted_modules,
                "extraction_method": "AI-Powered (Groq API)",
                "processing_info": {
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                },
                "stats": {
                    "total_modules": len(formatted_modules),
                   "average_content_length": round(sum(len(m.get("content", "")) for m in formatted_modules) / len(formatted_modules)) if formatted_modules else 0,
                },
            }

        except Exception as e:
            error_message = str(e)
            print(f"Processing failed: {error_message}")
            return {
                "success": False,
                "error": error_message,
                "modules": [],
                "processing_info": {
                    "file_name": os.path.basename(file_path) if file_path else "unknown",
                    "error_type": e.__class__.__name__,
                },
            }

if __name__ == "__main__":
    # Example usage: Change the file name to test different syllabi
    SYLLABUS_FILE = "Syllabus.pdf" # <-- Change this to your test file

    if os.path.exists(SYLLABUS_FILE):
        try:
            processor = SyllabusProcessor()
            result = processor.process_syllabus(SYLLABUS_FILE)

            if result["success"]:
                print("\n--- Processing Successful ---")
                print(json.dumps(result, indent=2))
            else:
                print("\n--- Processing Failed ---")
                print(json.dumps(result, indent=2))
        except ValueError as e:
            print(f"Configuration Error: {e}")
    else:
        print(f"Please create or place '{SYLLABUS_FILE}' in the same directory to run the test.")