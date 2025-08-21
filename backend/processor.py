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

    # -----------------------------
    # Cleaning helpers
    # -----------------------------
    def _clean_syllabus_text(self, text: str) -> str:
        """Remove unnecessary syllabus headers/footers before module division"""

        # Remove Pre-Requisites section
        text = re.sub(r"Pre-?Requisite.*?(Module\s*\d+)", r"\1", text, flags=re.S | re.I)

        # Remove common table headings like "Module Content Hrs Marks"
        text = re.sub(r"Module\s*Content\s*Hrs\.?\s*Marks.*", "", text, flags=re.I)

        # Remove course codes like [PC(CS/IT)513]
        text = re.sub(r"\[[A-Z]+\(.+?\)\d+\]", "", text)

        # Remove standalone numbers on separate lines (like “1”, “2”)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.M)

        # Clean multiple spaces/newlines
        text = re.sub(r"\s+", " ", text)

        return text.strip()

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
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "is", "are", "was", "were", "this",
            "that", "page",
        }
        meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        if meaningful:
            title = " ".join(meaningful[:3]).title()
            return title if len(title) > 5 else "Course Content"
        return "Learning Module"

    # -----------------------------
    # File validation & extraction
    # -----------------------------
    def validate_pdf(self, file_path: str) -> bool:
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
        try:
            print(f"Reading text file: {os.path.basename(file_path)}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Text file read: {len(content):,} characters")
            return content
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            raise Exception(f"Error reading text file: {str(e)}")

    # -----------------------------
    # Module creation
    # -----------------------------
    def divide_into_modules(self, text: str) -> List[Dict[str, Any]]:
        modules: List[Dict[str, Any]] = []

        if not text or not text.strip():
            print("No text provided for module division")
            return []

        print("🧩 Starting module division...")

        patterns = [
            r"^\s*(?:chapter|unit|module|section|topic|lesson)\s*[:\-]?\s*\d+",
            r"^\s*week\s*[:\-]?\s*\d+",
            r"^\s*\d+\.\s+.+?$",
            r"^\s*(?:part|section)\s+[IVX]+",
            r"^\s*(?:day|session)\s+\d+",
        ]

        for i, pattern in enumerate(patterns):
            print(f"Trying pattern {i + 1}: {pattern}")
            sections = re.split(f"({pattern})", text, flags=re.IGNORECASE | re.MULTILINE)
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

    # -----------------------------
    # Main entry
    # -----------------------------
    def process_syllabus(self, file_path: str) -> Dict[str, Any]:
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

            # 🔥 NEW CLEANING STEP
            text = self._clean_syllabus_text(text)

            print(f"Text extraction successful: {len(text):,} characters extracted")
            print("Analyzing content structure and creating modules...")
            modules = self.divide_into_modules(text)

            if not modules:
                raise Exception("Could not create any modules from the text. The file may not contain structured content.")

            print(f"Created {len(modules)} learning modules")

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
                    "average_content_length": round(
                        sum(len(m["content"]) for m in modules) / len(modules)
                    )
                    if modules else 0,
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
    processor = SyllabusProcessor()
    result = processor.process_syllabus("./Syllabus.pdf")  # adjust path

    if result["success"]:
        print("\nStats:", result["stats"])
        for m in result["modules"]:
            print(f"\n=== {m['title']} ===")
            print(m["content"])
    else:
        print("\nFailed:", result["error"], result.get("processing_info", {}))
