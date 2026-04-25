"""
Image captioning using BLIP (Salesforce).
Model is loaded once and cached for performance.
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from app.utils import OUTPUTS_DIR, generate_id

_processor = None
_model     = None


def _load_model():
    global _processor, _model
    if _processor is None:
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _model     = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _model.eval()


def caption_image(image_path: str) -> str:
    """Generate a caption for an image. Returns caption string."""
    _load_model()

    image  = Image.open(image_path).convert("RGB")
    inputs = _processor(image, return_tensors="pt")

    with torch.no_grad():
        output = _model.generate(**inputs, max_length=60, num_beams=4)

    caption = _processor.decode(output[0], skip_special_tokens=True)

    # Save caption
    out_dir = OUTPUTS_DIR / "captions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{generate_id()}.txt"
    out_file.write_text(caption, encoding="utf-8")

    return caption


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(caption_image(sys.argv[1]))