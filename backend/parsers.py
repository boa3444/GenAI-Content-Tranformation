import os
import io
import logging
import PyPDF2
import docx
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

logger = logging.getLogger(__name__)

def parse_source_document(filename: str, content_bytes: bytes) -> dict:
    """
    Parses document content bytes and returns a dictionary with raw text and page_count.
    """
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    page_count = 1

    if ext == ".pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
            page_count = len(pdf_reader.pages)
            text_chunks = []
            for page in pdf_reader.pages:
                txt = page.extract_text()
                if txt:
                    text_chunks.append(txt)
            text = "\n\n".join(text_chunks)
        except Exception as e:
            logger.error(f"PDF Parsing Error: {e}")
            text = content_bytes.decode("utf-8", errors="ignore")
    elif ext in [".docx", ".doc"]:
        try:
            doc = docx.Document(io.BytesIO(content_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)
            # Estimate pages (~3000 chars per page)
            page_count = max(1, len(text) // 3000)
        except Exception as e:
            logger.error(f"DOCX Parsing Error: {e}")
            text = content_bytes.decode("utf-8", errors="ignore")
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
        if pytesseract:
            try:
                img = Image.open(io.BytesIO(content_bytes))
                text = pytesseract.image_to_string(img)
            except Exception as e:
                logger.error(f"OCR Error: {e}")
                text = f"[Image OCR Failed: {e}]"
        else:
            text = "[OCR Not Configured - Install Tesseract OCR]"
        page_count = 1
    else:
        text = content_bytes.decode("utf-8", errors="ignore")
        page_count = max(1, len(text) // 3000)

    return {
        "text": text,
        "page_count": page_count
    }
