"""Gemini reads the prescription photo, following the rules in PRESCRIPTION-OCR.txt."""
import io
import json
import os
from functools import cache
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image, ImageOps

# tried in order; the next one is used when a model fails (overloaded, out of quota, retired, timed out)
MODELS = [os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"), "gemini-3.5-flash", "gemini-flash-lite-latest"]
RULES = (Path(__file__).parent / "PRESCRIPTION-OCR.txt").read_text(encoding="utf-8")
COLS = ("medicine", "dosage", "frequency")
SCHEMA = {"type": "array", "items": {"type": "object", "required": list(COLS),
                                     "properties": {c: {"type": "string"} for c in COLS}}}


@cache
def _gemini():
    # reads GEMINI_API_KEY (or GOOGLE_API_KEY). One quick retry per model, then fall through to the next model.
    return genai.Client(http_options=types.HttpOptions(
        timeout=30_000, retry_options=types.HttpRetryOptions(attempts=2, initial_delay=1, max_delay=2)))


def _shrink(image_bytes: bytes) -> bytes:
    """Upright 1600px JPEG. Gemini reads it as well as a multi-MB photo and 2 to 3x faster."""
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(image_bytes))).convert("RGB")  # phones store rotation in EXIF
    im.thumbnail((1600, 1600))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=85)
    return out.getvalue()


def extract_prescription(image_bytes: bytes, filename: str) -> list[dict]:
    """Photo -> [{medicine, dosage, frequency}]. Raises on API failure; the UI shows the error state."""
    image = types.Part.from_bytes(data=_shrink(image_bytes), mime_type="image/jpeg")
    config = types.GenerateContentConfig(system_instruction=RULES, temperature=0,
                                         response_mime_type="application/json", response_schema=SCHEMA,
                                         automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
    for model in dict.fromkeys(MODELS):
        try:
            r = _gemini().models.generate_content(
                model=model, config=config,
                contents=[image, "Read this prescription."])
            break
        except Exception as e:
            if model == MODELS[-1]:
                raise
            print(f"gemini {model} failed ({str(e)[:80]}), trying next model")
    return [{c: str(row.get(c, "")).strip() for c in COLS} for row in json.loads(r.text)]


if __name__ == "__main__":  # live check: python -m backend.backend_ocr assets/samples/sample-1-fever.jpg
    import sys
    p = Path(sys.argv[1])
    print(json.dumps(extract_prescription(p.read_bytes(), p.name), indent=1))
