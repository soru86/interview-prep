from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def load_resume_text(resume_folder: Path) -> tuple[str, Path]:
    if not resume_folder.exists():
        raise FileNotFoundError(f"Resume folder not found: {resume_folder}")

    candidates = sorted(
        [
            path
            for path in resume_folder.iterdir()
            if path.is_file()
            and not path.name.startswith(".")
            and path.suffix.lower() in {".pdf", ".docx", ".doc", ".txt"}
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No resume found in {resume_folder}. Add a PDF, DOCX, or TXT file."
        )

    resume_path = candidates[0]
    suffix = resume_path.suffix.lower()
    if suffix == ".pdf":
        text = _read_pdf(resume_path)
    elif suffix in {".docx", ".doc"}:
        text = _read_docx(resume_path)
    else:
        text = resume_path.read_text(encoding="utf-8")

    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        raise ValueError(f"Resume file is empty or unreadable: {resume_path}")
    return cleaned, resume_path


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_docx(path: Path) -> str:
    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_json_object(text: str) -> dict:
    """Extract the first JSON object from LLM output (handles markdown/thinking blocks)."""
    _think = "<" + "think" + ">"
    _think_close = "<" + "/think" + ">"
    _reason = "<" + "redacted_reasoning" + ">"
    _reason_close = "<" + "/redacted_reasoning" + ">"
    for pattern in (
        _think + r".*?" + _think_close,
        _reason + r".*?" + _reason_close,
    ):
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(text[start : end + 1])
