import io


def extract_text_from_image(image_bytes):
    """Read text from a screenshot using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Screenshot analysis needs pillow and pytesseract installed."
        ) from exc

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise RuntimeError(
            "Could not read the image. Make sure the Tesseract OCR engine is installed."
        ) from exc
    
