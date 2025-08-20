import os
import re
import fitz  # type: ignore # PyMuPDF
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SyllabusProcessor:
    def __init__(self):
        self.nlp = None
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.perplexity_api_key:
            print("Warning: PERPLEXITY_API_KEY is not set. Fallback questions will be used.")
        print("SyllabusProcessor initialized with PyMuPDF and Perplexity AI")

    # ----------------------------
    # File validation and extraction
    # ----------------------------
    def validate_pdf(self, file_path: str) -> bool:
        """Validate PDF file before processing"""
        try:
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return False

            file_size = os.path.getsize(file_path)
            if file_size < 100:
                print(f"File too small ({file_size} bytes): {file_path}")
                return False

            print(f"File validation: {file_size:,} bytes")

            try:
                with fitz.open(file_path) as doc:
                    if doc.page_count == 0:
                        print("PDF has no pages")
                        return False
                    # Try to read first page
                    _ = doc[0].get_text()
                    print(f"PDF validation passed: {doc.page_count} pages")
                    return True
            except Exception as e:
                print(f"PDF validation failed: {e}")
                return False

        except Exception as e:
            print(f"PDF validation failed: {e}")
            return False

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF with simplified error handling"""
        try:
            print(f"Starting PDF extraction: {os.path.basename(file_path)}")
            if not self.validate_pdf(file_path):
                raise Exception("PDF validation failed - file may be corrupted or invalid")

            text = ""
            successful_pages = 0
            with fitz.open(file_path) as doc:
                print(f"Successfully opened PDF with {doc.page_count} pages")
                for page_num in range(doc.page_count):
                    try:
                        page = doc[page_num]
                        page_text = page.get_text()
                        if page_text and page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text + "\n"
                            successful_pages += 1
                        else:
                            print(f"Page {page_num + 1} appears to be empty")
                    except Exception as page_error:
                        print(f"Error extracting page {page_num + 1}: {page_error}")
                        continue

            print(f"Successfully processed {successful_pages} pages")
            if not text.strip():
                raise Exception("No readable text could be extracted from the PDF")

            print(f"Text extraction complete: {len(text):,} characters extracted")
            return text

        except Exception as e:
            print(f"PDF extraction failed: {str(e)}")
            raise Exception(f"Error extracting PDF text with PyMuPDF: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            print(f"Reading text file: {os.path.basename(file_path)}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Text file read: {len(content):,} characters")
            return content
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            raise Exception(f"Error reading text file: {str(e)}")

    # ----------------------------
    # Cleaning and titling helpers
    # ----------------------------
    def _clean_content(self, content: str) -> str:
        """Clean and format module content"""
        if not content:
            return ""

        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"Page \d+", "", content)
        content = re.sub(r"--- Page \d+ ---", "", content)
        content = re.sub(r"\n+", " ", content)

        if len(content) > 500:
            sentences = content.split(".")
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) < 450:
                    truncated += sentence.strip() + "."
                else:
                    break
            return truncated.strip() + "..."
        return content.strip()

    def _generate_title_from_content(self, content: str) -> str:
        """Generate a meaningful title from content"""
        if not content:
            return "Learning Module"
        words = content.split()[:8]
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "this",
            "that",
            "page",
        }
        meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        if meaningful:
            title = " ".join(meaningful[:3]).title()
            return title if len(title) > 5 else "Course Content"
        return "Learning Module"

    # ----------------------------
    # Module creation
    # ----------------------------
    def divide_into_modules(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced rule-based module division"""
        modules: List[Dict[str, Any]] = []

        if not text or not text.strip():
            print("No text provided for module division")
            return []

        print("🧩 Starting module division...")

        patterns = [
            r"(?im)^\s*(?:chapter|unit|module|section|topic|lesson)\s*[:\-]?\s*\d+",
            r"(?im)^\s*week\s*[:\-]?\s*\d+",
            r"(?im)^\s*\d+\.\s+.+?$",  # 1. Title
            r"(?im)^\s*(?:part|section)\s+[IVX]+",
            r"(?im)^\s*(?:day|session)\s+\d+",
        ]

        for i, pattern in enumerate(patterns):
            print(f"Trying pattern {i + 1}: {pattern}")
            sections = re.split(f"({pattern})", text)
            if len(sections) > 3:
                modules = []
                current_title = "Introduction"
                current_content = ""
                for section in sections:
                    if re.match(pattern, section or "", re.IGNORECASE | re.MULTILINE):
                        if current_content.strip():
                            modules.append(
                                {
                                    "id": f"module_{len(modules) + 1}",
                                    "title": current_title.strip(),
                                    "content": self._clean_content(current_content.strip()),
                                }
                            )
                        current_title = section.strip()
                        current_content = ""
                    else:
                        current_content += section or ""

                if current_content.strip():
                    modules.append(
                        {
                            "id": f"module_{len(modules) + 1}",
                            "title": current_title.strip(),
                            "content": self._clean_content(current_content.strip()),
                        }
                    )

                if len(modules) >= 2:
                    print(f"Successfully created {len(modules)} modules using pattern {i + 1}")
                    break

        if not modules:
            print("No patterns found, using fallback method...")
            modules = self._create_balanced_modules(text)

        modules = [m for m in modules if m["content"].strip()]
        print(f"Final result: {len(modules)} modules created")
        return modules[:6]

    def _create_balanced_modules(self, text: str) -> List[Dict[str, Any]]:
        """Create balanced modules when no patterns are found"""
        modules: List[Dict[str, Any]] = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        if len(paragraphs) < 4:
            sentences = [s.strip() for s in re.split(r"[.\n]+", text) if s.strip()]
            total_sentences = len(sentences)
            modules_count = min(4, max(2, total_sentences // 15))
            sentences_per_module = total_sentences // modules_count if modules_count > 0 else total_sentences

            for i in range(modules_count):
                start_idx = i * sentences_per_module
                end_idx = start_idx + sentences_per_module if i < modules_count - 1 else total_sentences
                module_sentences = sentences[start_idx:end_idx]
                content = ". ".join(module_sentences).strip()
                if content:
                    title = self._generate_title_from_content(content)
                    modules.append(
                        {
                            "id": f"module_{i + 1}",
                            "title": f"Module {i + 1}: {title}",
                            "content": self._clean_content(content),
                        }
                    )
        else:
            modules_count = min(4, max(2, len(paragraphs) // 3))
            paragraphs_per_module = len(paragraphs) // modules_count if modules_count > 0 else len(paragraphs)

            for i in range(modules_count):
                start_idx = i * paragraphs_per_module
                end_idx = start_idx + paragraphs_per_module if i < modules_count - 1 else len(paragraphs)
                module_paragraphs = paragraphs[start_idx:end_idx]
                content = "\n\n".join(module_paragraphs).strip()
                if content:
                    title = self._generate_title_from_content(content)
                    modules.append(
                        {
                            "id": f"module_{i + 1}",
                            "title": f"Module {i + 1}: {title}",
                            "content": self._clean_content(content),
                        }
                    )

        return modules

    # ----------------------------
    # Question generation and parsing
    # ----------------------------
    def generate_questions(self, module_content: str, module_title: str) -> List[Dict[str, Any]]:
        """Generate questions using Perplexity AI via requests, with graceful fallback"""
        try:
            print(f"Generating questions for: {module_title[:50]}...")

            if not self.perplexity_api_key:
                print("Using fallback questions (no PERPLEXITY_API_KEY)")
                return self.get_fallback_questions(module_title)

            prompt = f"""Based on this syllabus content about "{module_title}", generate exactly 5 questions:
1. One easy multiple choice question with 4 options
2. One medium multiple choice question with 4 options
3. One easy short answer question
4. One medium short answer question
5. One hard essay question
Content: {module_content[:1000]}
Format each question as:
Type: [multiple-choice/short-answer/essay]
Difficulty: [easy/medium/hard]
Question: [question text]
Options: [A) Option 1 B) Option 2 C) Option 3 D) Option 4] - only for multiple choice
---"""

            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator. Generate high-quality, relevant questions based on the provided syllabus content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 800,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.perplexity.ai/chat/completions", headers=headers, json=data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                questions_text = result["choices"][0]["message"]["content"].strip()
                parsed = self.parse_ai_questions(questions_text, module_title)
                if len(parsed) < 3:
                    print("AI generated too few questions, using fallback")
                    return self.get_fallback_questions(module_title)
                print(f"Generated {len(parsed)} Perplexity AI questions")
                return parsed
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return self.get_fallback_questions(module_title)

        except Exception as e:
            print(f"Perplexity API error: {e}")
            print("Falling back to demo questions")
            return self.get_fallback_questions(module_title)

    def parse_ai_questions(self, questions_text: str, module_title: str) -> List[Dict[str, Any]]:
        """Enhanced AI question parsing"""
        questions: List[Dict[str, Any]] = []
        sections = questions_text.split("---")
        for i, section in enumerate(sections[:5]):
            if not section.strip():
                continue
            q = self._parse_single_question(section.strip(), i + 1, module_title)
            if q:
                questions.append(q)
        return questions if questions else self.get_fallback_questions(module_title)

    def _parse_single_question(
        self, section: str, question_id: int, module_title: str
    ) -> Dict[str, Any] | None:
        """Parse a single question from AI response"""
        try:
            lines = [l.strip() for l in section.split("\n") if l.strip()]
            qtype, difficulty, qtext, options = "short-answer", "medium", "", []
            for line in lines:
                low = line.lower()
                if low.startswith("type:"):
                    qtype = line.split(":", 1)[1].strip().lower()
                elif low.startswith("difficulty:"):
                    difficulty = line.split(":", 1)[1].strip().lower()
                elif low.startswith("question:"):
                    qtext = line.split(":", 1)[1].strip()
                elif low.startswith("options:"):
                    opts_text = line.split(":", 1)[1].strip()
                    # capture A) ... B) ... C) ... D) ... robustly
                    options = [
                        o.strip()
                        for o in re.findall(r"\b[A-D]\)\s*([^A-D\)][^)]*)", opts_text)
                        if o.strip()
                    ]
            if qtext:
                out = {
                    "id": str(question_id),
                    "question": qtext,
                    "type": qtype if qtype in ["multiple-choice", "short-answer", "essay"] else "short-answer",
                    "difficulty": difficulty if difficulty in ["easy", "medium", "hard"] else "medium",
                }
                if out["type"] == "multiple-choice" and options:
                    out["options"] = options[:4]
                return out
        except Exception as e:
            print(f"Error parsing question {question_id}: {e}")
        return None

    def get_fallback_questions(self, module_title: str) -> List[Dict[str, Any]]:
        """Enhanced fallback questions for demo purposes"""
        clean_title = re.sub(r"Module \d+:?\s*", "", module_title).strip() or "this module"
        return [
            {
                "id": "1",
                "question": f"What are the key concepts covered in {clean_title}?",
                "type": "multiple-choice",
                "difficulty": "easy",
                "options": [
                    "Basic definitions and terminology",
                    "Advanced theoretical frameworks",
                    "Practical applications and examples",
                    "All of the above",
                ],
            },
            {
                "id": "2",
                "question": f"Which of the following best describes the main focus of {clean_title}?",
                "type": "multiple-choice",
                "difficulty": "medium",
                "options": ["Theoretical understanding", "Practical implementation", "Critical analysis", "Comprehensive overview"],
            },
            {
                "id": "3",
                "question": f"Explain the main learning objectives of {clean_title}.",
                "type": "short-answer",
                "difficulty": "easy",
            },
            {
                "id": "4",
                "question": f"Describe how the concepts in {clean_title} relate to real-world applications and provide specific examples.",
                "type": "short-answer",
                "difficulty": "medium",
            },
            {
                "id": "5",
                "question": f"Critically analyze the importance of {clean_title} in the broader curriculum and connect it to other modules.",
                "type": "essay",
                "difficulty": "hard",
            },
        ]

    # ----------------------------
    # Main entry
    # ----------------------------
    def process_syllabus(self, file_path: str) -> Dict[str, Any]:
        """Enhanced main processing function with comprehensive error handling"""
        try:
            print(f"Starting syllabus processing: {os.path.basename(file_path)}")
            print("Extracting text from file...")
            if file_path.lower().endswith(".pdf"):
                text = self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(".txt"):
                text = self.extract_text_from_txt(file_path)
            else:
                raise Exception("Unsupported file format. Please upload PDF or TXT files only.")

            if not text or not text.strip():
                raise Exception("No readable text found in the uploaded file")

            print(f"Text extraction successful: {len(text):,} characters extracted")
            print("Analyzing content structure and creating modules...")
            modules = self.divide_into_modules(text)

            if not modules:
                raise Exception("Could not create any modules from the text. The file may not contain structured content.")

            print(f"Created {len(modules)} learning modules")
            print("Generating questions for each module...")
            total_questions = 0
            for i, module in enumerate(modules):
                module_title = module["title"][:50] + "..." if len(module["title"]) > 50 else module["title"]
                print(f"Processing module {i + 1}/{len(modules)}: {module_title}")
                module["questions"] = self.generate_questions(module["content"], module["title"])
                total_questions += len(module["questions"])

            print(f"Processing complete! Generated {total_questions} total questions across {len(modules)} modules")

            return {
                "success": True,
                "original_text_length": len(text),
                "modules": modules,
                "extraction_method": "PyMuPDF",
                "processing_info": {
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                    "extraction_method": "PyMuPDF",
                },
                "stats": {
                    "total_modules": len(modules),
                    "total_questions": total_questions,
                    "average_questions_per_module": round(total_questions / len(modules), 1) if modules else 0,
                    "average_content_length": round(
                        sum(len(m["content"]) for m in modules) / len(modules)
                    )
                    if modules
                    else 0,
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


# ----------------------------
# Example usage (run as script)
# ----------------------------
if __name__ == "__main__":
    processor = SyllabusProcessor()
    result = processor.process_syllabus("./Syllabus.pdf")  # adjust path if needed

    if result["success"]:
        print("\nStats:", result["stats"])
        for m in result["modules"]:
            print(f"\n=== {m['title']} ===")
            print(m["content"])
            for q in m["questions"]:
                print("-", q["type"], q.get("difficulty"), q["question"], q.get("options", ""))
    else:
        print("\nFailed:", result["error"], result.get("processing_info", {}))
