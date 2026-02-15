"""
Detection service stubs.

Replace these placeholder implementations with actual model inference
once the ML models are integrated.
"""

import io

from PIL import Image
from PyPDF2 import PdfReader


async def detect_text(text: str) -> dict:
    """Detect AI-generated text. Placeholder implementation."""
    return {
        "content_type": "text",
        "ai_probability": 0.0,
        "analysis": "Model not loaded — placeholder response",
        "word_count": len(text.split()),
    }


async def detect_image(image_bytes: bytes) -> dict:
    """Detect AI-generated images. Placeholder implementation."""
    img = Image.open(io.BytesIO(image_bytes))
    return {
        "content_type": "image",
        "ai_probability": 0.0,
        "analysis": "Model not loaded — placeholder response",
        "dimensions": {"width": img.width, "height": img.height},
        "format": img.format,
    }


async def detect_audio(audio_bytes: bytes) -> dict:
    """Detect AI-generated audio. Placeholder implementation."""
    return {
        "content_type": "audio",
        "ai_probability": 0.0,
        "analysis": "Model not loaded — placeholder response",
        "size_bytes": len(audio_bytes),
    }


async def detect_pdf(pdf_bytes: bytes) -> dict:
    """Detect AI-generated content in PDFs. Placeholder implementation."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    return {
        "content_type": "pdf",
        "ai_probability": 0.0,
        "analysis": "Model not loaded — placeholder response",
        "page_count": len(reader.pages),
        "word_count": len(text.split()),
    }
