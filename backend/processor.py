from pypdf import PdfReader   
import openai
import re
from typing import List, Dict, Any
import os

# Set your OpenAI API key here (get from openai.com)
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

class SyllabusProcessor:
    def __init__(self):
        # Skip spaCy for now to avoid dependency issues
        self.nlp = None
        print("SyllabusProcessor initialized (running without spaCy for better compatibility)")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean and format module content"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove page numbers and headers
        content = re.sub(r'Page \d+', '', content)
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
        # Extract first few meaningful words
        words = content.split()[:8]
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'this', 'that'}
        meaningful_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        if meaningful_words:
            title = ' '.join(meaningful_words[:3]).title()
            return title if len(title) > 5 else "Course Content"
        return "Learning Module"
    
    def divide_into_modules(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced rule-based module division"""
        modules = []
        
        # Enhanced patterns for better recognition
        patterns = [
            r'(?i)(?:chapter|unit|module|section|topic|lesson)\s*[:\-]?\s*\d+',  # More flexible
            r'(?i)week\s*[:\-]?\s*\d+',  # Week patterns
            r'\d+\.\s*[A-Z][A-Za-z\s]{2,}',   # 1. INTRODUCTION, etc.
            r'(?i)(?:part|section)\s+[IVX]+',  # Roman numerals
            r'(?i)(?:day|session)\s+\d+',     # Day/Session patterns
        ]
        
        # Try to split by patterns
        for pattern in patterns:
            sections = re.split(f'({pattern})', text)  # Keep delimiters
            if len(sections) > 3:  # Need at least 2 modules
                modules = []
                current_title = "Introduction"
                current_content = ""
                
                for i, section in enumerate(sections):
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
                    break
        
        # Enhanced fallback with better content distribution
        if not modules:
            modules = self._create_balanced_modules(text)
        
        return modules[:6]  # Limit to 6 modules for prototype
    
    def _create_balanced_modules(self, text: str) -> List[Dict[str, Any]]:
        """Create balanced modules when no patterns are found"""
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 4:
            # Fall back to sentence-based splitting
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            total_sentences = len(sentences)
            modules_count = min(4, max(2, total_sentences // 15))  # 2-4 modules
            
            sentences_per_module = total_sentences // modules_count
            modules = []
            
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
            paragraphs_per_module = len(paragraphs) // modules_count
            modules = []
            
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
        """Generate questions using OpenAI (with enhanced fallback for demo)"""
        try:
            # If OpenAI API key is not set, use fallback questions
            if openai.api_key == "YOUR_OPENAI_API_KEY":
                return self.get_fallback_questions(module_title)
            
            prompt = f"""
Based on this syllabus content about "{module_title}", generate exactly 5 questions:
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
---
"""
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            # Parse response and format questions
            questions_text = response.choices[0].text.strip()
            parsed_questions = self.parse_ai_questions(questions_text, module_title)
            
            # Ensure we have enough questions
            if len(parsed_questions) < 3:
                return self.get_fallback_questions(module_title)
            
            return parsed_questions
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
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
                    # Parse options (A) B) C) D) format)
                    option_matches = re.findall(r'[A-D]\)\s*([^A-D\)]+?)(?=[A-D\)|\s*$)', options_text)
                    options = [opt.strip() for opt in option_matches if opt.strip()]
            
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
        clean_title = re.sub(r'Module \d+:?', '', module_title).strip()
        if not clean_title:
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
        """Enhanced main processing function with progress tracking"""
        try:
            print(f"🔄 Starting processing of: {os.path.basename(file_path)}")
            
            # Extract text based on file extension
            print("📄 Extracting text from file...")
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            else:
                text = self.extract_text_from_txt(file_path)
            
            if not text.strip():
                raise Exception("No text found in the uploaded file")
            
            print(f"✅ Extracted {len(text):,} characters of text")
            
            # Divide into modules
            print("🧩 Analyzing content structure and creating modules...")
            modules = self.divide_into_modules(text)
            print(f"✅ Created {len(modules)} learning modules")
            
            # Generate questions for each module
            print("❓ Generating questions for each module...")
            total_questions = 0
            for i, module in enumerate(modules):
                print(f"   Processing module {i+1}/{len(modules)}: {module['title'][:50]}...")
                module['questions'] = self.generate_questions(
                    module['content'], 
                    module['title']
                )
                total_questions += len(module['questions'])
            
            print(f"🎉 Processing complete! Generated {total_questions} total questions across {len(modules)} modules")
            
            return {
                'success': True,
                'original_text_length': len(text),
                'modules': modules,
                'stats': {
                    'total_modules': len(modules),
                    'total_questions': total_questions,
                    'average_questions_per_module': round(total_questions / len(modules), 1) if modules else 0,
                    'average_content_length': round(sum(len(m['content']) for m in modules) / len(modules)) if modules else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'modules': []
            }
