"""
main.py — FastAPI server for LinkedIn Carousel → PDF Converter.

Endpoints:
  POST /api/convert     — accepts { url: string }, scrapes carousel, returns PDF info
  GET  /api/download/{pdf_id}  — streams the generated PDF for download
"""

import os
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

from scraper import scrape_carousel
from pdf_generator import generate_pdf, OUTPUT_DIR

app = FastAPI(
    title="LinkedIn Carousel → PDF",
    description="Convert LinkedIn post carousel images into a downloadable PDF.",
    version="1.0.0",
)

# CORS — allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response models ----------

class ConvertRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_linkedin_url(cls, v: str) -> str:
        v = v.strip()
        pattern = r"https?://(www\.)?linkedin\.com/(posts|feed/update|pulse)/"
        if not re.match(pattern, v):
            raise ValueError(
                "Invalid LinkedIn URL. Expected a URL like "
                "https://www.linkedin.com/posts/... or "
                "https://www.linkedin.com/feed/update/..."
            )
        return v


class ConvertResponse(BaseModel):
    status: str
    message: str
    pdf_id: str | None = None
    total_slides: int = 0


# ---------- Endpoints ----------

@app.post("/api/convert", response_model=ConvertResponse)
def convert_post(req: ConvertRequest):
    """
    Scrape a LinkedIn carousel post and generate a PDF.

    This is a synchronous endpoint — the request will block while
    Playwright captures slides.  For a personal-use tool this is fine;
    for production you'd want background tasks (Celery, etc).
    """
    try:
        # Step 1: Scrape the carousel images
        progress_state = {"current": 0, "total": 0, "message": "Starting..."}

        def on_progress(current, total, message):
            progress_state["current"] = current
            progress_state["total"] = total
            progress_state["message"] = message

        image_paths = scrape_carousel(req.url, on_progress=on_progress)

        if not image_paths:
            raise HTTPException(
                status_code=400,
                detail="No slides were captured. The post may not contain a carousel/document, "
                       "or the page structure may have changed.",
            )

        # Step 2: Generate PDF
        pdf_path, pdf_id = generate_pdf(image_paths, delete_temp=True)

        return ConvertResponse(
            status="done",
            message=f"Successfully captured {len(image_paths)} slides and generated PDF.",
            pdf_id=pdf_id,
            total_slides=len(image_paths),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@app.get("/api/download/{pdf_id}")
def download_pdf(pdf_id: str):
    """Download a previously generated PDF by its ID."""
    # Sanitize the pdf_id to prevent path traversal
    if not re.match(r"^[a-f0-9\-]+$", pdf_id):
        raise HTTPException(status_code=400, detail="Invalid PDF ID format.")

    pdf_path = OUTPUT_DIR / f"{pdf_id}.pdf"

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF not found. It may have been cleaned up or the ID is invalid.",
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"linkedin_carousel_{pdf_id[:8]}.pdf",
    )


@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
