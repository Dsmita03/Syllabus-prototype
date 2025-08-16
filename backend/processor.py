import fitz    # type: ignore - PyMuPDF
import requests
import re
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class SyllabusProcessor:
    def __init__(self):
        self.nlp = None
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is not set.")
        print("SyllabusProcessor initialized with PyMuPDF and Perplexity AI")

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
            
            # Quick validation without keeping document open
            try:
                with fitz.open(file_path) as doc:
                    if doc.page_count == 0:
                        print("PDF has no pages")
                        return False
                    
                    # Try to read first page
                    first_page = doc[0]
                    test_text = first_page.get_text()
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

            # Validate PDF first
            if not self.validate_pdf(file_path):
                raise Exception("PDF validation failed - file may be corrupted or invalid")
            
            # Extract text using context manager
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
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"Text file read: {len(content):,} characters")
            return content
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            raise Exception(f"Error reading text file: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean and format module content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove page numbers and headers
        content = re.sub(r'Page \d+', '', content)
        content = re.sub(r'--- Page \d+ ---', '', content)
        content = re.sub(r'\n+', ' ', content)
        
        # Limit content length for display
        if len(content) > 500:
            # Try to cut at sentence boundary
            sentences = content.split('.')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) < 450:
                    truncated += sentence + "."
                else:
                    break
            return truncated.strip() + "..."
        return content.strip()
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a meaningful title from content"""
        if not content:
            return "Learning Module"
        
        # Extract first few meaningful words
        words = content.split()[:8]
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'this', 'that', 'page'}
        meaningful_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        if meaningful_words:
            title = ' '.join(meaningful_words[:3]).title()
            return title if len(title) > 5 else "Course Content"
        return "Learning Module"
    
    def divide_into_modules(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced rule-based module division"""
        modules = []
        
        if not text or not text.strip():
            print("No text provided for module division")
            return []
        
        print("🧩 Starting module division...")
        
        # Enhanced patterns for better recognition
        patterns = [
            r'(?i)(?:chapter|unit|module|section|topic|lesson)\s*[:\-]?\s*\d+',  # More flexible
            r'(?i)week\s*[:\-]?\s*\d+',  # Week patterns
            r'\d+\.\s*[A-Z][A-Za-z\s]{2,}',   # 1. INTRODUCTION, etc.
            r'(?i)(?:part|section)\s+[IVX]+',  # Roman numerals
            r'(?i)(?:day|session)\s+\d+',     # Day/Session patterns
        ]
        
        # Try to split by patterns
        for i, pattern in enumerate(patterns):
            print(f"Trying pattern {i+1}: {pattern}")
            sections = re.split(f'({pattern})', text)  # Keep delimiters
            if len(sections) > 3:  # Need at least 2 modules
                print(f"Pattern {i+1} found {len(sections)} sections")
                modules = []
                current_title = "Introduction"
                current_content = ""
                
                for section in sections:
                    if re.match(pattern, section, re.IGNORECASE):
                        # Save previous module if exists
                        if current_content.strip():
                            modules.append({
                                'id': f"module_{len(modules)+1}",
                                'title': current_title.strip(),
                                'content': self._clean_content(current_content.strip())
                            })
                        current_title = section.strip()
                        current_content = ""
                    else:
                        current_content += section
                
                # Add final module
                if current_content.strip():
                    modules.append({
                        'id': f"module_{len(modules)+1}",
                        'title': current_title.strip(),
                        'content': self._clean_content(current_content.strip())
                    })
                
                if modules and len(modules) >= 2:
                    print(f"Successfully created {len(modules)} modules using pattern {i+1}")
                    break
        
        # Enhanced fallback with better content distribution
        if not modules:
            print("No patterns found, using fallback method...")
            modules = self._create_balanced_modules(text)
        
        # Filter out empty modules
        modules = [m for m in modules if m['content'].strip()]
        
        print(f"Final result: {len(modules)} modules created")
        return modules[:6]  # Limit to 6 modules for prototype
    
    def _create_balanced_modules(self, text: str) -> List[Dict[str, Any]]:
        """Create balanced modules when no patterns are found"""
        modules = []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 4:
            # Fall back to sentence-based splitting
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            total_sentences = len(sentences)
            modules_count = min(4, max(2, total_sentences // 15))  # 2-4 modules
            
            sentences_per_module = total_sentences // modules_count if modules_count > 0 else total_sentences
            
            for i in range(modules_count):
                start_idx = i * sentences_per_module
                end_idx = start_idx + sentences_per_module if i < modules_count - 1 else total_sentences
                
                module_sentences = sentences[start_idx:end_idx]
                content = '. '.join(module_sentences).strip()
                
                if content:
                    title = self._generate_title_from_content(content)
                    modules.append({
                        'id': f"module_{i+1}",
                        'title': f"Module {i+1}: {title}",
                        'content': self._clean_content(content)
                    })
        else:
            # Use paragraph-based splitting
            modules_count = min(4, max(2, len(paragraphs) // 3))
            paragraphs_per_module = len(paragraphs) // modules_count if modules_count > 0 else len(paragraphs)
            
            for i in range(modules_count):
                start_idx = i * paragraphs_per_module
                end_idx = start_idx + paragraphs_per_module if i < modules_count - 1 else len(paragraphs)
                
                module_paragraphs = paragraphs[start_idx:end_idx]
                content = '\n\n'.join(module_paragraphs).strip()
                
                if content:
                    title = self._generate_title_from_content(content)
                    modules.append({
                        'id': f"module_{i+1}",
                        'title': f"Module {i+1}: {title}",
                        'content': self._clean_content(content)
                    })
        
        return modules
    
    def generate_questions(self, module_content: str, module_title: str) -> List[Dict[str, Any]]:
        """Generate questions using Perplexity AI via requests"""
        try:
            print(f"Generating questions for: {module_title[:50]}...")
            
            # Check if Perplexity API key is set
            if not self.perplexity_api_key or self.perplexity_api_key == "YOUR_PERPLEXITY_API_KEY":
                print("🔄 Using fallback questions (no Perplexity API key)")
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
            
            # Using requests to call Perplexity API
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "You are an expert educational content creator. Generate high-quality, relevant questions based on the provided syllabus content."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                questions_text = result['choices'][0]['message']['content'].strip()
                parsed_questions = self.parse_ai_questions(questions_text, module_title)
                
                # Ensure we have enough questions
                if len(parsed_questions) < 3:
                    print("AI generated too few questions, using fallback")
                    return self.get_fallback_questions(module_title)
                
                print(f"Generated {len(parsed_questions)} Perplexity AI questions")
                return parsed_questions
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return self.get_fallback_questions(module_title)
            
        except Exception as e:
            print(f"Perplexity API error: {e}")
            print("Falling back to demo questions")
            return self.get_fallback_questions(module_title)
    
    def parse_ai_questions(self, questions_text: str, module_title: str) -> List[Dict[str, Any]]:
        """Enhanced AI question parsing"""
        questions = []
        sections = questions_text.split('---')
        
        for i, section in enumerate(sections[:5]):
            if not section.strip():
                continue
                
            question_data = self._parse_single_question(section.strip(), i+1, module_title)
            if question_data:
                questions.append(question_data)
        
        return questions if questions else self.get_fallback_questions(module_title)
    
    def _parse_single_question(self, section: str, question_id: int, module_title: str) -> Dict[str, Any]:
        """Parse a single question from AI response"""
        try:
            lines = section.split('\n')
            question_type = 'short-answer'
            difficulty = 'medium'
            question_text = ""
            options = []
            
            for line in lines:
                line = line.strip()
                if line.lower().startswith('type:'):
                    question_type = line.split(':', 1)[1].strip().lower()
                elif line.lower().startswith('difficulty:'):
                    difficulty = line.split(':', 1)[1].strip().lower()
                elif line.lower().startswith('question:'):
                    question_text = line.split(':', 1)[1].strip()
                elif line.lower().startswith('options:'):
                    options_text = line.split(':', 1)[1].strip()
                    # Fixed: Better option parsing
                    options = re.findall(r'[A-D]\)\s*([^A-D\)]+)', options_text)
                    options = [opt.strip() for opt in options if opt.strip()]
            
            if question_text:
                result = {
                    'id': str(question_id),
                    'question': question_text,
                    'type': question_type if question_type in ['multiple-choice', 'short-answer', 'essay'] else 'short-answer',
                    'difficulty': difficulty if difficulty in ['easy', 'medium', 'hard'] else 'medium'
                }
                
                if options and question_type == 'multiple-choice' and len(options) >= 2:
                    result['options'] = options[:4]  # Limit to 4 options
                
                return result
                
        except Exception as e:
            print(f"Error parsing question {question_id}: {e}")
        
        # Return None if parsing failed
        return None
    
    def get_fallback_questions(self, module_title: str) -> List[Dict[str, Any]]:
        """Enhanced fallback questions for demo purposes"""
        # Extract key topics from module title for more relevant questions
        clean_title = re.sub(r'Module \d+:?\s*', '', module_title).strip()
        if not clean_title or clean_title.lower() == 'page':
            clean_title = "this module"
        
        return [
            {
                'id': '1',
                'question': f'What are the key concepts covered in {clean_title}?',
                'type': 'multiple-choice',
                'difficulty': 'easy',
                'options': ['Basic definitions and terminology', 'Advanced theoretical frameworks', 'Practical applications and examples', 'All of the above']
            },
            {
                'id': '2',
                'question': f'Which of the following best describes the main focus of {clean_title}?',
                'type': 'multiple-choice',
                'difficulty': 'medium',
                'options': ['Theoretical understanding', 'Practical implementation', 'Critical analysis', 'Comprehensive overview']
            },
            {
                'id': '3',
                'question': f'Explain the main learning objectives of {clean_title}.',
                'type': 'short-answer',
                'difficulty': 'easy'
            },
            {
                'id': '4',
                'question': f'Describe how the concepts in {clean_title} relate to real-world applications and provide specific examples.',
                'type': 'short-answer',
                'difficulty': 'medium'
            },
            {
                'id': '5',
                'question': f'Critically analyze the importance of {clean_title} in the broader context of the curriculum. Discuss its impact on student learning outcomes and how it connects to other course modules.',
                'type': 'essay',
                'difficulty': 'hard'
            }
        ]
    
    def process_syllabus(self, file_path: str) -> Dict[str, Any]:
        """Enhanced main processing function with comprehensive error handling"""
        try:
            print(f"Starting syllabus processing: {os.path.basename(file_path)}")
            
            # Extract text based on file extension
            print("Extracting text from file...")
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith('.txt'):
                text = self.extract_text_from_txt(file_path)
            else:
                raise Exception(f"Unsupported file format. Please upload PDF or TXT files only.")
            
            if not text or not text.strip():
                raise Exception("No readable text found in the uploaded file")

            print(f"Text extraction successful: {len(text):,} characters extracted")

            # Divide into modules
            print("Analyzing content structure and creating modules...")
            modules = self.divide_into_modules(text)
            
            if not modules:
                raise Exception("Could not create any modules from the text. The file may not contain structured content.")
            
            print(f"Created {len(modules)} learning modules")
            
            # Generate questions for each module
            print("Generating questions for each module...")
            total_questions = 0
            for i, module in enumerate(modules):
                module_title = module['title'][:50] + "..." if len(module['title']) > 50 else module['title']
                print(f"Processing module {i+1}/{len(modules)}: {module_title}")
                
                module['questions'] = self.generate_questions(
                    module['content'], 
                    module['title']
                )
                total_questions += len(module['questions'])
            
            print(f"Processing complete! Generated {total_questions} total questions across {len(modules)} modules")
            
            return {
                'success': True,
                'original_text_length': len(text),
                'modules': modules,
                'extraction_method': 'PyMuPDF',
                'processing_info': {
                    'file_name': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'extraction_method': 'PyMuPDF'
                },
                'stats': {
                    'total_modules': len(modules),
                    'total_questions': total_questions,
                    'average_questions_per_module': round(total_questions / len(modules), 1) if modules else 0,
                    'average_content_length': round(sum(len(m['content']) for m in modules) / len(modules)) if modules else 0
                }
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"Processing failed: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'modules': [],
                'processing_info': {
                    'file_name': os.path.basename(file_path) if file_path else 'unknown',
                    'error_type': type(e).__name__  # Fixed: __name__ instead of **name**
                }
            }
