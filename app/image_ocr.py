"""
OCR using Tesseract via pytesseract.
"""
import pytesseract
from PIL import Image
from app.utils import OUTPUTS_DIR, generate_id


def run_ocr(image_path: str) -> str:
    """Extract text from image using Tesseract OCR. Returns extracted text."""
    image = Image.open(image_path)

    # Improve OCR accuracy with config
    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(image, config=custom_config)
    text = text.strip()

    # Save OCR output
    out_dir = OUTPUTS_DIR / "ocr"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{generate_id()}.txt"
    out_file.write_text(text, encoding="utf-8")

    return text


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run_ocr(sys.argv[1]))