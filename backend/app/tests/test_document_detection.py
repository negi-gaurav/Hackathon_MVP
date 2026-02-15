"""
Tests for the document detection endpoint and underlying heuristics.

Two main scenarios:
  1. A real photograph (JPEG with EXIF) → should NOT be flagged as synthetic.
  2. A screenshot-like image (PNG, no EXIF, monitor resolution) → should be flagged.
  3. Unit tests for individual heuristic functions.
  4. Integration test via the FastAPI test client.
"""

import io
import struct

import numpy as np
import pytest
from PIL import Image
from PyPDF2 import PdfWriter

from app.services.document_detector import (
    analyze_noise_patterns,
    detect_document,
    detect_inconsistent_fonts,
    extract_exif_metadata,
)


# ---------------------------------------------------------------------------
# Helpers to create test images
# ---------------------------------------------------------------------------


def _make_real_photo_jpeg() -> bytes:
    """Create a JPEG with realistic noise and EXIF-like properties.

    We add varying noise across the image to mimic a real photograph and
    set DPI to a typical camera value.
    """
    rng = np.random.RandomState(42)
    # Gradient base (simulates a real scene with varying brightness)
    base = np.tile(np.linspace(30, 220, 640, dtype=np.uint8), (480, 1))
    # Add spatially varying noise (more noise in darker regions)
    noise = rng.normal(0, 15, (480, 640)).astype(np.float64)
    noise[:240, :] *= 2  # top half is noisier
    arr = np.clip(base.astype(np.float64) + noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr, mode="L")

    # Inject basic EXIF data (Make, Model)
    from PIL.ExifTags import Base as ExifBase

    exif = img.getexif()
    exif[ExifBase.Make] = "Canon"
    exif[ExifBase.Model] = "EOS R5"

    buf = io.BytesIO()
    img.save(buf, format="JPEG", dpi=(300, 300), exif=exif.tobytes())
    return buf.getvalue()


def _make_screenshot_png() -> bytes:
    """Create a PNG that looks like a screenshot.

    - Exact 1920×1080 resolution
    - No EXIF
    - Very uniform 'noise' (solid colour blocks)
    """
    # Flat colour blocks (like a UI screenshot)
    arr = np.zeros((1080, 1920, 3), dtype=np.uint8)
    arr[:, :, 0] = 45   # dark background
    arr[:, :, 1] = 45
    arr[:, :, 2] = 48
    # Add a 'toolbar' area at the top
    arr[:60, :, :] = [55, 55, 58]

    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_simple_pdf() -> bytes:
    """Create a minimal PDF with one page of text."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Unit tests — individual heuristics
# ---------------------------------------------------------------------------


class TestExifExtraction:
    def test_jpeg_with_exif(self):
        data = _make_real_photo_jpeg()
        img = Image.open(io.BytesIO(data))
        exif = extract_exif_metadata(img)
        assert "Make" in exif
        assert exif["Make"] == "Canon"

    def test_png_no_exif(self):
        data = _make_screenshot_png()
        img = Image.open(io.BytesIO(data))
        exif = extract_exif_metadata(img)
        assert exif == {}


class TestNoiseAnalysis:
    def test_uniform_image_high_uniformity(self):
        """A solid-colour image should have very high noise uniformity."""
        arr = np.full((256, 256), 128, dtype=np.uint8)
        img = Image.fromarray(arr, mode="L")
        result = analyze_noise_patterns(img)
        assert result["noise_uniformity"] >= 0.9

    def test_varied_noise_lower_uniformity(self):
        """An image with spatially varying noise should have lower uniformity."""
        rng = np.random.RandomState(99)
        arr = np.zeros((256, 256), dtype=np.float64)
        # Left half: low noise
        arr[:, :128] = 128 + rng.normal(0, 2, (256, 128))
        # Right half: high noise
        arr[:, 128:] = 128 + rng.normal(0, 40, (256, 128))
        arr = np.clip(arr, 0, 255).astype(np.uint8)

        img = Image.fromarray(arr, mode="L")
        result = analyze_noise_patterns(img)
        # Should be notably less uniform than the solid image
        assert result["noise_uniformity"] < 0.8


class TestPdfFonts:
    def test_blank_pdf_no_fonts(self):
        data = _make_simple_pdf()
        result = detect_inconsistent_fonts(data)
        assert result["total_unique_fonts"] == 0
        assert result["inconsistent"] is False


# ---------------------------------------------------------------------------
# Integration tests — full scoring pipeline
# ---------------------------------------------------------------------------


class TestDocumentScoring:
    @pytest.mark.asyncio
    async def test_real_photo_low_score(self):
        """A realistic JPEG with EXIF and varied noise should score low."""
        data = _make_real_photo_jpeg()
        result = await detect_document(data, "image/jpeg")

        assert result["is_synthetic"] is False
        assert result["confidence"] < 0.5
        assert isinstance(result["reasons"], list)
        assert isinstance(result["metadata"], dict)

    @pytest.mark.asyncio
    async def test_screenshot_high_score(self):
        """A screenshot-like PNG should score high (flagged as suspicious)."""
        data = _make_screenshot_png()
        result = await detect_document(data, "image/png")

        assert result["is_synthetic"] is True
        assert result["confidence"] >= 0.5
        # Should mention missing EXIF and/or noise uniformity
        reasons_text = " ".join(result["reasons"]).lower()
        assert "exif" in reasons_text or "noise" in reasons_text or "screen" in reasons_text

    @pytest.mark.asyncio
    async def test_blank_pdf(self):
        """A blank PDF with no text or fonts should be somewhat suspicious."""
        data = _make_simple_pdf()
        result = await detect_document(data, "application/pdf")

        assert isinstance(result["is_synthetic"], bool)
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["reasons"], list)
        assert len(result["reasons"]) > 0  # should flag something

    @pytest.mark.asyncio
    async def test_response_schema(self):
        """Verify the response contains all required fields."""
        data = _make_screenshot_png()
        result = await detect_document(data, "image/png")

        assert "is_synthetic" in result
        assert "confidence" in result
        assert "reasons" in result
        assert "metadata" in result
        assert isinstance(result["is_synthetic"], bool)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["reasons"], list)
        assert isinstance(result["metadata"], dict)


# ---------------------------------------------------------------------------
# FastAPI endpoint integration test
# ---------------------------------------------------------------------------


class TestDocumentEndpoint:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def test_upload_jpeg(self, client):
        data = _make_real_photo_jpeg()
        response = client.post(
            "/api/v1/detect/document",
            files={"file": ("photo.jpg", io.BytesIO(data), "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "is_synthetic" in body
        assert "confidence" in body
        assert "reasons" in body
        assert "metadata" in body

    def test_upload_png_screenshot(self, client):
        data = _make_screenshot_png()
        response = client.post(
            "/api/v1/detect/document",
            files={"file": ("screenshot.png", io.BytesIO(data), "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_synthetic"] is True
        assert body["confidence"] >= 0.5

    def test_upload_pdf(self, client):
        data = _make_simple_pdf()
        response = client.post(
            "/api/v1/detect/document",
            files={"file": ("doc.pdf", io.BytesIO(data), "application/pdf")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "is_synthetic" in body

    def test_reject_invalid_type(self, client):
        response = client.post(
            "/api/v1/detect/document",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 400
