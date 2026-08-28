"""
pdf_generator.py — Creates a PDF from a list of slide images.

Each image becomes one PDF page sized to match the image's native aspect ratio
(no cropping or stretching).  After the PDF is saved, the temporary images
folder is deleted.
"""

import os
import shutil
import uuid
from pathlib import Path

from PIL import Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# Output directory for generated PDFs
OUTPUT_DIR = Path(__file__).parent / "output"


def _ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_pdf(image_paths: list[str], delete_temp: bool = True) -> tuple[str, str]:
    """
    Generate a PDF from a list of image file paths.

    Args:
        image_paths:  Ordered list of absolute paths to slide images.
        delete_temp:  If True, deletes the parent directory of the images
                      after PDF creation (assumes all images are in the same
                      temp folder).

    Returns:
        Tuple of (pdf_file_path, pdf_id).
    """
    _ensure_output_dir()

    if not image_paths:
        raise ValueError("No images provided for PDF generation.")

    pdf_id = str(uuid.uuid4())
    pdf_path = str(OUTPUT_DIR / f"{pdf_id}.pdf")

    # Sort images by filename to ensure correct order
    sorted_paths = sorted(image_paths, key=lambda p: os.path.basename(p))

    # Create the PDF
    # We'll set the initial page size to the first image's dimensions,
    # then adjust for each subsequent page.
    c = canvas.Canvas(pdf_path)

    for img_path in sorted_paths:
        try:
            with Image.open(img_path) as img:
                img_width, img_height = img.size

                # Convert pixels to points (72 points per inch).
                # Assume 150 DPI for a good balance of quality and file size.
                dpi = 150
                page_width = (img_width / dpi) * 72
                page_height = (img_height / dpi) * 72

                # Ensure minimum readable size — at least 8 inches wide
                min_width = 8 * 72  # 8 inches in points
                if page_width < min_width:
                    scale = min_width / page_width
                    page_width *= scale
                    page_height *= scale

                c.setPageSize((page_width, page_height))
                c.drawImage(
                    img_path,
                    0,
                    0,
                    width=page_width,
                    height=page_height,
                    preserveAspectRatio=True,
                    anchor='c',
                )
                c.showPage()

        except Exception as e:
            print(f"[pdf_generator] Warning: could not process {img_path}: {e}")
            continue

    c.save()
    print(f"[pdf_generator] PDF saved to {pdf_path}")

    # Clean up temporary images
    if delete_temp and image_paths:
        temp_dir = os.path.dirname(image_paths[0])
        if temp_dir and os.path.isdir(temp_dir) and "linkedin_slides_" in temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[pdf_generator] Cleaned up temp directory: {temp_dir}")

    return pdf_path, pdf_id
