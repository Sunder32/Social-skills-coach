"""
Document Loader for Training
Parses PDF, DOCX, TXT files for training data
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re


class DocumentLoader:
    """
    Loads and processes documents for training
    Supports: PDF, DOCX, TXT, EPUB
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.epub', '.md'}
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Args:
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_file(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Load a single file and extract text
        
        Returns:
            Tuple of (text_content, metadata)
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
        
        metadata = {
            "filename": path.name,
            "extension": extension,
            "source": str(path)
        }
        
        text = ""
        
        if extension == '.pdf':
            text = self._load_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            text = self._load_docx(file_path)
        elif extension == '.txt':
            text = self._load_txt(file_path)
        elif extension == '.md':
            text = self._load_txt(file_path)  # Markdown as plain text
        elif extension == '.epub':
            text = self._load_epub(file_path)
        
        return text, metadata
    
    def _load_pdf(self, file_path: str) -> str:
        """Load PDF file"""
        text_parts = []
        
        # Try PyMuPDF first (best for complex PDFs and Russian text)
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            for page in doc:
                text = page.get_text()
                if text:
                    text_parts.append(text)
            doc.close()
            
            if text_parts:
                result = "\n\n".join(text_parts)
                if self._is_readable_text(result):
                    return result
        except ImportError:
            pass
        except Exception:
            pass
        
        # Try pdfplumber second (better for Russian text)
        try:
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            if text_parts:
                result = "\n\n".join(text_parts)
                if self._is_readable_text(result):
                    return result
        except ImportError:
            pass
        except Exception:
            pass
        
        # Fallback to pypdf
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Try to fix encoding issues
                    text = self._fix_encoding(text)
                    text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except ImportError:
            raise ImportError("pypdf not installed. Run: pip install pypdf")
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
    
    def _is_readable_text(self, text: str) -> bool:
        """Check if text looks readable (not garbled)"""
        if not text:
            return False
        
        # Count alphanumeric and Cyrillic characters
        readable_chars = sum(1 for c in text if c.isalnum() or '\u0400' <= c <= '\u04FF' or c.isspace())
        return readable_chars > len(text) * 0.5
    
    def _fix_encoding(self, text: str) -> str:
        """Try to fix common encoding issues in PDF text"""
        # Check if text looks like mojibake (garbled encoding)
        # Common pattern: Cyrillic text incorrectly decoded
        
        # Try to detect if it's garbled CP1251
        try:
            # If text contains many unusual characters, try re-encoding
            unusual_chars = sum(1 for c in text if ord(c) > 1000 or (128 <= ord(c) < 256))
            if unusual_chars > len(text) * 0.3:  # More than 30% unusual chars
                # Try Latin-1 -> CP1251 conversion (common PDF issue)
                try:
                    fixed = text.encode('latin-1').decode('cp1251')
                    # Verify it looks like Cyrillic now
                    cyrillic_chars = sum(1 for c in fixed if '\u0400' <= c <= '\u04FF')
                    if cyrillic_chars > len(fixed) * 0.3:
                        return fixed
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
                
                # Try raw bytes interpretation
                try:
                    fixed = text.encode('raw_unicode_escape').decode('cp1251')
                    cyrillic_chars = sum(1 for c in fixed if '\u0400' <= c <= '\u04FF')
                    if cyrillic_chars > len(fixed) * 0.3:
                        return fixed
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        except Exception:
            pass
        
        return text
    
    def _load_docx(self, file_path: str) -> str:
        """Load DOCX file"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            return "\n\n".join(text_parts)
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        except Exception as e:
            raise Exception(f"Error reading DOCX: {e}")
    
    def _load_txt(self, file_path: str) -> str:
        """Load TXT file"""
        encodings = ['utf-8', 'cp1251', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise Exception(f"Could not decode file with any known encoding")
    
    def _load_epub(self, file_path: str) -> str:
        """Load EPUB file"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(file_path)
            text_parts = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    if text.strip():
                        text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except ImportError:
            raise ImportError("ebooklib and beautifulsoup4 not installed. Run: pip install ebooklib beautifulsoup4")
        except Exception as e:
            raise Exception(f"Error reading EPUB: {e}")
    
    def load_directory(self, dir_path: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Load all supported files from a directory
        
        Returns:
            List of (text_content, metadata) tuples
        """
        documents = []
        path = Path(dir_path)
        
        if not path.exists():
            raise ValueError(f"Directory not found: {dir_path}")
        
        for file_path in path.rglob("*"):
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    text, metadata = self.load_file(str(file_path))
                    if text.strip():
                        documents.append((text, metadata))
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing
        """
        # Clean text
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph is too long, split by sentences
                if len(para) > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sent in sentences:
                        if len(current_chunk) + len(sent) < self.chunk_size:
                            current_chunk += sent + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent + " "
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_training_data(
        self,
        documents: List[Tuple[str, Dict[str, Any]]],
        output_path: str,
        data_type: str = "knowledge"
    ) -> str:
        """
        Convert documents to training data format
        
        Args:
            documents: List of (text, metadata) tuples
            output_path: Path to save JSONL file
            data_type: Type of data (knowledge, conversation, qa)
            
        Returns:
            Path to created file
        """
        training_examples = []
        
        for text, metadata in documents:
            chunks = self.chunk_text(text)
            
            for i, chunk in enumerate(chunks):
                if data_type == "knowledge":
                    # Knowledge format - for RAG
                    example = {
                        "content": chunk,
                        "title": metadata.get("filename", ""),
                        "source": metadata.get("source", ""),
                        "chunk_index": i,
                        "topic": self._detect_topic(chunk)
                    }
                elif data_type == "qa":
                    # Q&A format - generate questions
                    questions = self._generate_questions(chunk)
                    for q in questions:
                        example = {
                            "instruction": "Ответь на вопрос на основе текста.",
                            "input": q,
                            "output": chunk,
                            "source": metadata.get("filename", "")
                        }
                        training_examples.append(example)
                    continue
                else:
                    # Conversation format
                    example = {
                        "instruction": "Используй эту информацию для помощи в общении.",
                        "input": "",
                        "output": chunk,
                        "source": metadata.get("filename", "")
                    }
                
                training_examples.append(example)
        
        # Save to JSONL
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in training_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        return output_path
    
    def _detect_topic(self, text: str) -> str:
        """Simple topic detection based on keywords"""
        topics = {
            "конфликт": ["конфликт", "спор", "ссора", "разногласи", "противореч"],
            "переговоры": ["переговор", "договор", "сделка", "торг", "компромисс"],
            "отношения": ["отношен", "любов", "дружб", "семь", "близк"],
            "работа": ["работ", "коллег", "начальн", "офис", "карьер"],
            "эмоции": ["эмоци", "чувств", "настроен", "страх", "тревог", "злост"],
            "общение": ["общен", "разговор", "беседа", "коммуникац", "диалог"]
        }
        
        text_lower = text.lower()
        
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return topic
        
        return "общее"
    
    def _generate_questions(self, text: str) -> List[str]:
        """Generate simple questions from text (placeholder for LLM generation)"""
        # This is a simple placeholder - in production, use LLM to generate questions
        questions = []
        
        # Extract potential topics
        if "как" in text.lower():
            questions.append("Какой совет даётся в этом тексте?")
        if "важно" in text.lower():
            questions.append("Что важно учитывать согласно тексту?")
        if "нужно" in text.lower() or "следует" in text.lower():
            questions.append("Что рекомендуется делать?")
        
        if not questions:
            questions.append("О чём говорится в тексте?")
        
        return questions


def process_books_for_training(
    input_dir: str,
    output_dir: str,
    chunk_size: int = 1000
) -> Dict[str, str]:
    """
    Process all books/documents in a directory for training
    
    Args:
        input_dir: Directory with source documents
        output_dir: Directory to save processed data
        chunk_size: Size of text chunks
        
    Returns:
        Dict with paths to created files
    """
    loader = DocumentLoader(chunk_size=chunk_size)
    
    # Load all documents
    documents = loader.load_directory(input_dir)
    
    if not documents:
        raise ValueError(f"No supported documents found in {input_dir}")
    
    print(f"Loaded {len(documents)} documents")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create different data formats
    results = {}
    
    # Knowledge data for RAG
    knowledge_path = os.path.join(output_dir, "knowledge_data.jsonl")
    loader.create_training_data(documents, knowledge_path, data_type="knowledge")
    results["knowledge"] = knowledge_path
    
    # SFT training data
    sft_path = os.path.join(output_dir, "sft_data.jsonl")
    loader.create_training_data(documents, sft_path, data_type="conversation")
    results["sft"] = sft_path
    
    print(f"Created training data:")
    for key, path in results.items():
        print(f"  {key}: {path}")
    
    return results
