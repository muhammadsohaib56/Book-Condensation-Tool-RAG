import pypdfium2 as pdfium
import pytesseract
from PIL import Image
import io
import re
import logging

logger = logging.getLogger(__name__)

def clean_ocr_text(text):
    """Clean OCR text by removing metadata and artifacts."""
    text = re.sub(r"<CONTENT_FROM_OCR>.*?</CONTENT_FROM_OCR>", "", text, flags=re.DOTALL)
    text = re.sub(r"\.\.\.\(truncated \d+ characters\)\.\.\.", "", text)
    text = re.sub(r"[\n\s]+", " ", text).strip()
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove non-ASCII chars
    return text

def ocr_page_image(page, page_num):
    """Perform OCR on a page rendered as an image."""
    try:
        bitmap = page.render(scale=2.0)  # Higher scale for better OCR
        pil_image = bitmap.to_pil()
        text = pytesseract.image_to_string(pil_image)
        cleaned_text = clean_ocr_text(text)
        if not cleaned_text:
            logger.warning(f"OCR extracted empty text from page {page_num}")
        return cleaned_text
    except Exception as e:
        logger.error(f"OCR failed for page {page_num}: {e}")
        return ""

def load_book(pdf_path):
    """Load and clean text from PDF using pypdfium2 with OCR fallback."""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        pages = []
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text_page = page.get_textpage()
            text = text_page.get_text_range()
            cleaned_text = clean_ocr_text(text)
            if not cleaned_text:
                logger.warning(f"No text extracted from page {page_num + 1}, attempting OCR...")
                cleaned_text = ocr_page_image(page, page_num + 1)
            if cleaned_text:
                pages.append(cleaned_text)
            else:
                logger.warning(f"Skipping empty page {page_num + 1}")
        pdf.close()
        if not pages:
            raise ValueError("No text extracted from PDF")
        return pages
    except Exception as e:
        logger.error(f"Error loading PDF: {str(e)}")
        raise

def split_into_sections(pages):
    """Split pages into sections based on book structure."""
    sections = []
    current_section = {"title": None, "content": ""}
    section_titles = [
        r"\bPROLOGUE\b",
        r"\bPART\s+(I|II|III|IV|V)\b",
        r"\bCHAPTER\s+\d+\.?\s*",
        r"\bEPILOGUE\b",
        r"\bAcknowledgments\b",
        r"\bNotes\b",
        r"\bIndex\b",
        r"\bABOUT THE AUTHOR\b"
    ]
    section_counter = 0

    for page in pages:
        if not page.strip():
            continue
        page_upper = page.upper()
        for title_pattern in section_titles:
            if re.search(title_pattern, page_upper):
                if current_section["content"]:
                    section_counter += 1
                    current_section["title"] = current_section["title"] or f"Section {section_counter}"
                    sections.append(current_section)
                    current_section = {"title": None, "content": ""}
                match = re.search(title_pattern, page_upper)
                current_section["title"] = match.group(0).title()
                current_section["content"] = page
                break
        else:
            current_section["content"] += " " + page

    if current_section["content"]:
        section_counter += 1
        current_section["title"] = current_section["title"] or f"Section {section_counter}"
        sections.append(current_section)

    # Filter out empty sections
    sections = [s for s in sections if s["content"].strip()]
    logger.info(f"Extracted {len(sections)} sections")
    return sections