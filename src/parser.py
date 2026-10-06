import re
import os
from pathlib import Path
from typing import Optional, Tuple, List

class ResumeParser:
    """Robust multi-format resume parser supporting PDF, DOCX, and TXT with layout preservation."""
    
    @staticmethod
    def extract_text_and_links_from_pdf(file_path: Path) -> Tuple[str, List[str]]:
        text = ""
        links: List[str] = []
        
        # 1. Try pdfplumber first for text + hyperlinks
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True) or page.extract_text() or ""
                    text += page_text + "\n"
                    
                    # Extract clickable annotation links
                    if hasattr(page, "hyperlinks") and page.hyperlinks:
                        for hl in page.hyperlinks:
                            uri = hl.get("uri")
                            if uri:
                                links.append(uri)
            if text.strip():
                return text, links
        except Exception:
            pass

        # 2. Fallback to pypdf with annotation parsing
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
                
                # Check annotations (/Annots) in pypdf
                if "/Annots" in page:
                    annots = page["/Annots"]
                    for annot in annots:
                        try:
                            obj = annot.get_object()
                            if "/A" in obj and "/URI" in obj["/A"]:
                                links.append(str(obj["/A"]["/URI"]))
                        except Exception:
                            continue
        except Exception as e:
            raise ValueError(f"Failed to parse PDF with all engines: {str(e)}")

        return text, links

    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return ""
        except Exception:
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: Path) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @classmethod
    def parse_file(cls, file_path: Path) -> Tuple[Optional[str], Optional[str], List[str]]:
        """Parses any supported resume file. Returns (text, error_message, extracted_links)."""
        suffix = file_path.suffix.lower()
        links: List[str] = []
        try:
            if suffix == ".pdf":
                text, links = cls.extract_text_and_links_from_pdf(file_path)
            elif suffix in [".docx", ".doc"]:
                text = cls.extract_text_from_docx(file_path)
            elif suffix == ".txt":
                text = cls.extract_text_from_txt(file_path)
            else:
                return None, f"Unsupported file extension: {suffix}", []
                
            if not text.strip():
                return None, "File parsed but contained no readable text.", []
                
            return text.strip(), None, links
        except Exception as e:
            return None, str(e), []

    @staticmethod
    def extract_github_url(text: str) -> Optional[str]:
        """Extracts a GitHub profile URL from text, preserving its original form."""
        match = re.search(
            r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9-]+/?',
            text,
            re.IGNORECASE,
        )
        return match.group(0) if match else None

    @staticmethod
    def extract_github_username(text: str, embedded_links: Optional[List[str]] = None) -> Optional[str]:
        """Extracts public GitHub username from text or embedded hyperlink annotations."""
        all_targets = [text] + (embedded_links or [])
        
        for target in all_targets:
            match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-_]+)', target, re.IGNORECASE)
            if match:
                username = match.group(1).strip().rstrip('/')
                if username.lower() not in ["join", "features", "explore", "about", "pricing", "topics"]:
                    return username
        return None

    @staticmethod
    def extract_candidate_name_fallback(text: str, default_name: str) -> str:
        """Heuristic fallback to extract candidate name from top lines."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            first_line = lines[0]
            if 2 <= len(first_line.split()) <= 4 and not any(kw in first_line.lower() for kw in ["resume", "curriculum", "page", "cv"]):
                return first_line
        return default_name
