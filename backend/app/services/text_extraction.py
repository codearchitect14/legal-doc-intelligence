from pathlib import Path

import docx
import easyocr
import pymupdf as fitz

_ocr_reader: easyocr.Reader | None = None

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def _get_ocr_reader() -> easyocr.Reader:
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(["en"], gpu=False)
    return _ocr_reader


def _ocr_image_bytes(image_bytes: bytes) -> str:
    results = _get_ocr_reader().readtext(image_bytes, detail=0)
    return "\n".join(results)


def _extract_pdf(file_path: Path) -> tuple[str, str]:
    """Returns (text, ocr_status). Pages without a text layer are OCR'd."""
    doc = fitz.open(file_path)
    try:
        page_texts: list[str] = []
        ocr_used = False
        for page in doc:
            text = page.get_text().strip()
            if text:
                page_texts.append(text)
                continue
            pixmap = page.get_pixmap()
            page_texts.append(_ocr_image_bytes(pixmap.tobytes("png")))
            ocr_used = True
        return "\n\n".join(page_texts), ("completed" if ocr_used else "not_required")
    finally:
        doc.close()


def _extract_docx(file_path: Path) -> tuple[str, str]:
    document = docx.Document(file_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return text, "not_required"


def _extract_image(file_path: Path) -> tuple[str, str]:
    return _ocr_image_bytes(file_path.read_bytes()), "completed"


def extract_text(file_path: str) -> tuple[str, str]:
    """Extract text from a stored file. Returns (text, ocr_status)."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix in IMAGE_EXTENSIONS:
        return _extract_image(path)
    raise ValueError(f"Unsupported file type for text extraction: {suffix}")
