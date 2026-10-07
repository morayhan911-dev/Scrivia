"""Scrivia backend. Gemini reads the photo, Groq writes the report and answers chat.
app.py imports exactly these five functions. Keys come from backend/env (or backend/.env)."""
from pathlib import Path

from dotenv import load_dotenv

for _f in ("env", ".env"):
    load_dotenv(Path(__file__).parent / _f)

from .backend_groq import chat_reply  # noqa: E402
from .backend_ocr import extract_prescription  # noqa: E402
from .report_generator import generate_report, report_pdf  # noqa: E402
from .safety import check_medicine  # noqa: E402
