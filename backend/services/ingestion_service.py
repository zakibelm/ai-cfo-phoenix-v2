import logging
import hashlib
import io
from typing import BinaryIO, Dict, Any
from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for document ingestion and text extraction"""
    
    @staticmethod
    def compute_file_hash(file_content: bytes) -> str:
        """Compute SHA256 hash of file"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def extract_text_from_pdf(file: BinaryIO) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(file)
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file: BinaryIO) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from DOCX")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file: BinaryIO) -> str:
        """Extract text from TXT file"""
        try:
            content = file.read()
            
            # Try UTF-8 first, then fallback to latin-1
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')
            
            logger.info(f"Extracted {len(text)} characters from TXT")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting TXT text: {str(e)}")
            raise ValueError(f"Failed to extract text from TXT: {str(e)}")
    
    @staticmethod
    def extract_text_from_csv(file: BinaryIO) -> str:
        """Extract text from CSV file"""
        try:
            import csv
            content = file.read()
            
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('latin-1')
            
            # Parse CSV and convert to readable text
            csv_reader = csv.reader(io.StringIO(text_content))
            rows = list(csv_reader)
            
            if not rows:
                return ""
            
            # Format as table-like text
            text_parts = []
            headers = rows[0] if rows else []
            text_parts.append(" | ".join(headers))
            text_parts.append("-" * 50)
            
            for row in rows[1:]:
                text_parts.append(" | ".join(str(cell) for cell in row))
            
            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from CSV")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting CSV text: {str(e)}")
            raise ValueError(f"Failed to extract text from CSV: {str(e)}")
    
    @classmethod
    def extract_text(cls, file: BinaryIO, filename: str) -> str:
        """Extract text from file based on extension"""
        extension = filename.lower().split('.')[-1]
        
        extractors = {
            'pdf': cls.extract_text_from_pdf,
            'docx': cls.extract_text_from_docx,
            'doc': cls.extract_text_from_docx,
            'txt': cls.extract_text_from_txt,
            'md': cls.extract_text_from_txt,
            'csv': cls.extract_text_from_csv
        }
        
        extractor = extractors.get(extension)
        if not extractor:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return extractor(file)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        # Join with proper spacing
        cleaned = '\n\n'.join(lines)
        
        return cleaned
    
    @classmethod
    def process_document(cls, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """Process document: extract, clean, and prepare metadata"""
        try:
            # Read file content
            file.seek(0)
            file_content = file.read()
            file_hash = cls.compute_file_hash(file_content)
            
            # Extract text
            file.seek(0)
            raw_text = cls.extract_text(file, filename)
            
            # Clean text
            cleaned_text = cls.clean_text(raw_text)
            
            if not cleaned_text or len(cleaned_text) < 10:
                raise ValueError("Extracted text is too short or empty")
            
            return {
                "text": cleaned_text,
                "sha256": file_hash,
                "size_bytes": len(file_content),
                "char_count": len(cleaned_text),
                "word_count": len(cleaned_text.split())
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise
