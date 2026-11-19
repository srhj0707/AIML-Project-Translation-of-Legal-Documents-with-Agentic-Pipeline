"""
Universal Legal Document Parser for Eng2भारत.
Extracts clean legal text from:
  - Plain Text (.txt)
  - PDF Legal Briefs & Petitions (.pdf via pypdf)
  - Microsoft Word Documents (.docx via python-docx)
  - Scanned Legal Documents & Images (.png, .jpg, .jpeg, .webp via EasyOCR / PIL)
"""

import io
import os
import re
from pathlib import Path
from typing import Optional, Tuple

# PDF Support
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Word .docx Support
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Image OCR Support
try:
    import easyocr
    from PIL import Image
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


_ocr_reader_instance = None

def get_ocr_reader():
    """Lazy-loads EasyOCR English reader instance for OCR performance."""
    global _ocr_reader_instance
    if _ocr_reader_instance is None and EASYOCR_AVAILABLE:
        # Load English model on CPU without downloading redundant GPU libs
        _ocr_reader_instance = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _ocr_reader_instance


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decodes plain text using common encodings."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]:
        try:
            text = file_bytes.decode(enc)
            if text and text.strip():
                return text.strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode plain text file with supported encodings.")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text page-by-page from PDF document using pypdf."""
    if not PYPDF_AVAILABLE:
        raise RuntimeError("pypdf is not installed. Please install pypdf to process PDF files.")

    stream = io.BytesIO(file_bytes)
    reader = pypdf.PdfReader(stream)
    
    if len(reader.pages) == 0:
        raise ValueError("The uploaded PDF has no readable pages.")

    extracted_pages = []
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        if page_text:
            extracted_pages.append(page_text)

    if not extracted_pages:
        raise ValueError(
            "The PDF appears to be a scanned image without a native text layer. "
            "Please upload the document as an image (.png/.jpg) for OCR extraction or upload a searchable PDF."
        )

    return "\n\n".join(extracted_pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts structured text from Microsoft Word .docx files."""
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx is not installed. Please install python-docx to process .docx files.")

    stream = io.BytesIO(file_bytes)
    doc = docx.Document(stream)
    
    text_parts = []
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            text_parts.append(t)

    # Also capture table contents if present
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                text_parts.append(" | ".join(row_cells))

    if not text_parts:
        raise ValueError("The uploaded .docx document does not contain readable text.")

    return "\n\n".join(text_parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    """Extracts text from scanned legal images using EasyOCR."""
    if not EASYOCR_AVAILABLE:
        raise RuntimeError("EasyOCR / Pillow is not installed. Please install easyocr to enable image OCR.")

    try:
        reader = get_ocr_reader()
        if reader is None:
            raise RuntimeError("EasyOCR reader initialization failed.")

        # Pass bytes directly to easyocr
        results = reader.readtext(file_bytes, detail=0, paragraph=True)
        if not results:
            # Fallback to line-by-line reading
            results = reader.readtext(file_bytes, detail=0, paragraph=False)

        extracted_text = "\n\n".join(str(r).strip() for r in results if str(r).strip())
        if not extracted_text:
            raise ValueError("No recognizable English legal text was detected in the uploaded image.")

        return extracted_text

    except Exception as e:
        if "No recognizable" in str(e):
            raise
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def parse_legal_document(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Universal dispatcher for extracting text from uploaded legal files.
    Returns:
        (extracted_text, document_format_type)
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty (0 bytes).")

    ext = Path(filename).suffix.lower()

    if ext in [".txt", ".text"]:
        return extract_text_from_txt(file_bytes), "Plain Text (.txt)"

    elif ext == ".pdf":
        return extract_text_from_pdf(file_bytes), "Portable Document Format (.pdf)"

    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_bytes), "Microsoft Word (.docx)"

    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        return extract_text_from_image(file_bytes), f"Legal Scan Image ({ext.upper()})"

    else:
        # Attempt plain text decoding as fallback
        try:
            return extract_text_from_txt(file_bytes), f"Raw Text ({ext})"
        except Exception:
            raise ValueError(
                f"Unsupported file format '{ext}'. Eng2भारत supports: .txt, .pdf, .docx, and images (.png, .jpg, .jpeg, .webp)."
            )
