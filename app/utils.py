from pathlib import Path
from datetime import datetime

BASE_DIR    = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def save_bytes(folder: Path, filename: str, data: bytes) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    # Sanitize filename
    safe_name = Path(filename).name
    path = folder / f"{generate_id()}_{safe_name}"
    path.write_bytes(data)
    return path