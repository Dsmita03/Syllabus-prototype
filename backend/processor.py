# ==============================================================================
# AI-Powered Syllabus Processor (Using Groq Cloud API)
# ==============================================================================
# This script uses an advanced "master prompt" with multiple examples to handle
# a wide variety of unstructured syllabus formats using a robust OCR and
# digital text extraction pipeline. It does NOT require nougat-ocr.
#
# Setup Instructions:
# 1.  Go to https://console.groq.com/keys and sign up for a free account.
# 2.  Create a new API key and copy it.
# 3.  In Google Colab, use the "Secrets" tab (key icon) to add a new secret:
#     Name: GROQ_API_KEY
#     Value: your_key_here
#
# Required Installations:
# -----------------------
# pip install PyMuPDF pdf2image pytesseract opencv-python requests python-dotenv
#
# System Dependencies (for Colab/Linux):
# -------------------------------------
# sudo apt-get install tesseract-ocr poppler-utils
# ==============================================================================

import os
import requests
import json
from typing import List, Dict, Any
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
GROQ_MODEL_NAME = "llama3-8b-8192"
# DPI for rendering PDF pages to images for OCR
OCR_DPI = 300


class SyllabusProcessor:
    def __init__(self):
        """
        Initializes the processor, loading the Groq API key from environment variables.
        """
        # For Google Colab, it's better to use the userdata library
        try:
            self.api_key =os.getenv("GROQ_API_KEY")
            print("Loaded GROQ_API_KEY from Colab Secrets.")
        except (ImportError, KeyError):
            self.api_key = os.getenv("GROQ_API_KEY")
            if self.api_key:
                print("Loaded GROQ_API_KEY from .env file.")
            else:
                 raise ValueError("GROQ_API_KEY not found. Please set it in Colab Secrets or a .env file.")

        print("SyllabusProcessor initialized with Groq API.")

    # ==============================================================================
    # PART I: ROBUST PDF & TEXT EXTRACTION
    # ==============================================================================

    def _extract_text_from_digital_pdf(self, pdf_path: str) -> (str, bool):
        """
        Extracts text from a digital PDF file, preserving block structure.
        """
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                for b in blocks:
                    full_text += b[4] + "\n"

            is_successful = len(full_text.strip()) > 200
            print(f"Digital extraction yielded {len(full_text.strip())} characters.")
            return full_text, is_successful
        except Exception as e:
            print(f"Error processing {pdf_path} with PyMuPDF: {e}")
            return "", False

    def _ocr_scanned_pdf(self, pdf_path: str) -> (str, bool):
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
        Hybrid pipeline to extract text from a PDF. It tries digital extraction
        first and falls back to OCR if the initial attempt fails.
        """
        print("Step 1: Attempting digital text extraction...")
        text, success = self._extract_text_from_digital_pdf(pdf_path)
        if success:
            print("Successfully extracted digital text. Skipping OCR.")
            return text

        print("\nDigital extraction failed or yielded poor results. Falling back to OCR...")
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

    # ==============================================================================
    # PART II: AI-POWERED MODULE EXTRACTION (ADVANCED PROMPT)
    # ==============================================================================

    def _extract_modules_with_llm(self, syllabus_text: str) -> List[Dict[str, Any]]:
        """
        Sends the syllabus text to the Groq API to extract modules.
        The prompt has been significantly enhanced with new examples to handle diverse formats.
        """
        print("\nStep 2: Sending text to Groq API for module extraction...")

        system_prompt = """
You are an expert academic data extraction system. Your task is to extract all modules, units, or weekly topics from a given university syllabus text into a structured JSON format.

**Instructions:**
1. Identify each distinct module, unit, or topic. These can be in lists, tables, paragraphs, or numbered outlines.
2. For each module, extract the module number (if available), title, and a description. If the title is descriptive enough, the description can be the same as the title.
3. Adhere strictly to the JSON schema provided. Do not add extra keys.
4. If a piece of information is not available, use a `null` value.
5. If no modules are found, return a JSON object with an empty "modules" array.
6. Your entire output must be a single, valid JSON object and nothing else.

**JSON Schema:**
{
  "modules": [
    {
      "module_number": "string or null",
      "module_title": "string",
      "description": "string",
      "learning_outcome": "string or null"
    }
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
    {
      "module_number": null,
      "module_title": "Introduction to Graph Theory",
      "description": "Definitions and Examples, Subgraphs, Complement of a graph, Graph Isomorphism."
    },
    {
      "module_number": null,
      "module_title": "Path, Cycles, Coloring",
      "description": "Walk, Trail, Path, Cycle, Euler Trails and Circuits, Planar Graphs."
    }
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
    {
      "module_number": "1",
      "module_title": "CPU structure and functions",
      "description": "CPU structure and functions, processor organization, ALU, data paths."
    },
    {
      "module_number": "2",
      "module_title": "Processor control",
      "description": "Processor control, micro-operations, instruction fetch, hardwired control."
    }
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
    {
      "module_number": "1",
      "module_title": "Information, Data, Data Types, ADT",
      "description": "Information, Data, Data Types, Abstract Data Type (ADT), Data Structure."
    },
    {
      "module_number": "2",
      "module_title": "Array as an ADT",
      "description": "Array as an ADT, Single and Multidimensional Arrays, Structures, Sparse Matrix."
    },
    {
      "module_number": "3",
      "module_title": "Pointers and Linked Lists",
      "description": "Pointers, ADT Linked List, Singly Linked List, Doubly Linked List."
    }
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
    {
      "module_number": "I.1",
      "module_title": "UNIT-I: Introduction to anatomy",
      "description": "Introduction to anatomy, anatomical terms, planes, organization of human body."
    },
    {
      "module_number": "I.2",
      "module_title": "UNIT-I: Musculo-skeletal system",
      "description": "Musculo-skeletal system: Types of bones, structure & divisions of the skeleton system."
    },
    {
      "module_number": "II.1",
      "module_title": "UNIT-II: Anatomy of Circulatory system",
      "description": "Anatomy of Circulatory system: General plan of circulatory system and its components."
    }
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
    {
      "module_number": "1",
      "module_title": "Ordinary Differential Equations (ODE)",
      "description": "Second order non- homogenous differential equations with constant coefficients."
    },
    {
      "module_number": "2",
      "module_title": "Partial Differential Equations (PDE)",
      "description": "Formation of partial differential equations - Singular integrals."
    }
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
    {
      "module_number": null,
      "module_title": "Regular Expression Tools (e.g Awk)",
      "description": "Regular Expression Tools (e.g Awk)"
    },
    {
      "module_number": null,
      "module_title": "Lex and Yacc",
      "description": "Lex and Yacc"
    },
    {
      "module_number": null,
      "module_title": "Bash Scripting",
      "description": "Bash Scripting"
    }
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
    {
      "module_number": null,
      "module_title": "Thermodynamics",
      "description": "C, and C,: definition and relation; adiabatic changes; reversible and irreversible processes."
    },
    {
      "module_number": null,
      "module_title": "Second law thermodynamics",
      "description": "Joule Thomson and throttling processes; inversion temperature."
    },
    {
      "module_number": null,
      "module_title": "Industrial Chemistry",
      "description": "Solid, liquid and gaseous fuels; constituents of coal, carbonization of coal."
    },
    {
        "module_number": null,
        "module_title": "Electrochemistry",
        "description": "Conductance of electrolytic solutions, specific conductance."
    }
  ]
}

---
**Example 8 (Highly Structured Table Format - NEW & MOST RELEVANT):**
Text: '''
"Unit No.","Topics to be Covered","Lecture Hours","Learning Outcome"
"1","Introduction: Need of compilers; Cousins of compilers; Compiler writing tools, compiler phases.","2","The students will be introduced with the language translator, their need and various phases of a compiler."
"2","Lexical analysis: Tokens, regular expressions, transition diagrams, Design of lexical analyzer generator.","5","Students will be familiar with various elements of a scanner (lexical analyzer). They will also learn how to use transition diagram or finite automata for designing a new lexical analyzer"
'''
JSON Output:
{
  "modules": [
    {
      "module_number": "1",
      "topics_covered": "Introduction: Need of compilers; Cousins of compilers; Compiler writing tools, compiler phases.",
      "lecture_hours": 2,
      "learning_outcome": "The students will be introduced with the language translator, their need and various phases of a compiler."
    },
    {
      "module_number": "2",
      "topics_covered": "Lexical analysis: Tokens, regular expressions, transition diagrams, Design of lexical analyzer generator.",
      "lecture_hours": 5,
      "learning_outcome": "Students will be familiar with various elements of a scanner (lexical analyzer). They will also learn how to use transition diagram or finite automata for designing a new lexical analyzer"
    }
  ]
}

---
**Example 9 (Paragraph Block Format - NEW & RELEVANT):**
Text: '''
SECTION-1
Introduction: Introduction to web technology, Internet and WWW, web site planning and design issues, HTML5: structure of html document, commenting, formatting tags, list tags, hyperlink tags, image, table tags, frame tags, form tags, CSS, Bootstrap, JSON(6Hrs)
Client Side Technologies: JavaScript: Overview of JavaScript, Data types, Control Structures, Arrays, Functions and Scopes, Objects in JS, Form validation, DOM: Introduction, DOMlevels, DOM Objects, their properties and methods, Manipulating DOM (6 Mrs)
JQuery: Introduction, Loading JQuery, selecting elements, changing styles, creating elements, appending elements, removing elements, handling events. (2 Hrs)
'''
JSON Output:
{
  "modules": [
    {
      "module_number": null,
      "module_title": "Introduction",
      "description": "Introduction to web technology, Internet and WWW, web site planning and design issues, HTML5: structure of html document, commenting, formatting tags, list tags, hyperlink tags, image, table tags, frame tags, form tags, CSS, Bootstrap, JSON(6Hrs)"
    },
    {
      "module_number": null,
      "module_title": "Client Side Technologies",
      "description": "JavaScript: Overview of JavaScript, Data types, Control Structures, Arrays, Functions and Scopes, Objects in JS, Form validation, DOM: Introduction, DOMlevels, DOM Objects, their properties and methods, Manipulating DOM (6 Mrs)"
    },
    {
      "module_number": null,
      "module_title": "JQuery",
      "description": "Introduction, Loading JQuery, selecting elements, changing styles, creating elements, appending elements, removing elements, handling events. (2 Hrs)"
    }
  ]
}

---
**Example 10 (Highly Structured Document - MOST COMPREHENSIVE):**
Text: '''
BMAT102L Differential Equations and Transforms
Pre-requisite BMAT101L
Course Objectives
1. To impart the knowledge of Laplace transform...
Course Outcomes
1. Find solution for second and higher order differential equations...
Module:1 Ordinary Differential Equations (ODE) 6 hours
Second order non- homogenous differential equations...
Text Book(s)
1. Erwin Kreyszig, Advanced Engineering Mathematics...
'''
JSON Output:
{
  "modules": [
    {
      "module_number": "1",
      "module_title": "Ordinary Differential Equations (ODE)",
      "lecture_hours": 6,
      "description": "Second order non- homogenous differential equations..."
    }
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

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=300)
            response.raise_for_status()

            response_data = response.json()
            json_output_str = response_data['choices'][0]['message']['content']

            extracted_data = json.loads(json_output_str)
            print("Successfully extracted structured data from Groq API.")

            return extracted_data.get("modules", [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request to Groq failed: {e}")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Failed to parse JSON from Groq response: {e}")
            print(f"Raw response from model: {response.text}")
            raise Exception("The AI model returned an invalid or unexpected format.")

    # ==============================================================================
    # PART III: MAIN PROCESSING WORKFLOW
    # ==============================================================================
    def process_syllabus(self, file_path: str) -> Dict[str, Any]:
        """
        Executes the full, AI-powered pipeline from file to structured module data.
        """
        try:
            print(f"Starting AI-powered syllabus processing: {os.path.basename(file_path)}")

            print("Extracting text from file...")
            if file_path.lower().endswith(".pdf"):
                text = self._get_text_from_pdf(file_path)
            elif file_path.lower().endswith(".txt"):
                text = self._extract_text_from_txt(file_path)
            else:
                raise Exception("Unsupported file format.")

            if not text or not text.strip():
                raise Exception("No readable text found in the uploaded file")

            print(f"Text extraction successful: {len(text):,} characters extracted")

            print("Analyzing content with AI and creating modules...")
            modules = self._extract_modules_with_llm(text)

            if not modules:
                raise Exception("AI could not identify any modules from the text.")

            print(f"AI successfully created {len(modules)} learning modules")

            formatted_modules = []
            for i, mod in enumerate(modules):
                # *** FIX IS HERE ***
                # Handle cases where the description is null (None) from the API
                content = mod.get("description") or "No description available."
                formatted_modules.append({
                    "id": f"module_{i + 1}",
                    "title": mod.get("module_title", "Untitled Module"),
                    "content": content
                })

            return {
                "success": True,
                "original_text_length": len(text),
                "modules": formatted_modules,
                "extraction_method": "AI-Powered (Groq API)",
                "processing_info": {
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                },
                "stats": {
                    "total_modules": len(formatted_modules),
                    "average_content_length": round(
                        sum(len(m["content"]) for m in formatted_modules) / len(formatted_modules)
                    ) if formatted_modules else 0,
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
    # Example usage:
    # 1. Make sure you have a file named 'Syllabus.pdf' in the same directory.
    # 2. Make sure you have set your GROQ_API_KEY in Colab Secrets or a .env file.
    if os.path.exists("Udaipur.pdf"):
        try:
            processor = SyllabusProcessor()
            result = processor.process_syllabus("Udaipur.pdf")

            if result["success"]:
                print("\n--- Processing Successful ---")
                print(json.dumps(result, indent=2))
            else:
                print("\n--- Processing Failed ---")
                print(json.dumps(result, indent=2))
        except ValueError as e:
            print(f"Configuration Error: {e}")
    else:
        print("Please create a 'Udaipur.pdf' file to run the test.")
