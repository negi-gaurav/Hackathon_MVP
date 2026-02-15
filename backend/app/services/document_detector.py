"""
Document detection service.

Analyzes uploaded documents (images and PDFs) using heuristic checks
to determine whether they are synthetic / AI-generated.

Heuristics (MVP — no ML model required):
  - Missing or suspicious EXIF metadata
  - Inconsistent DPI values
  - Perfect noise uniformity (synthetic images tend to have very uniform noise)
  - Screenshot indicators in metadata
  - Inconsistent fonts in PDFs
"""

import io
import math
import struct
from typing import Any

import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
from PyPDF2 import PdfReader


# ---------------------------------------------------------------------------
# EXIF metadata extraction
# ---------------------------------------------------------------------------

def extract_exif_metadata(image: Image.Image) -> dict[str, Any]:
    """Return a dict of human-readable EXIF tags from a PIL Image."""
    exif_data = image.getexif()
    if not exif_data:
        return {}
    metadata: dict[str, Any] = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))
        # Convert bytes to hex string for JSON serialisability
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8", errors="replace")
            except Exception:
                value = value.hex()
        metadata[tag_name] = value
    return metadata


# ---------------------------------------------------------------------------
# Noise analysis
# ---------------------------------------------------------------------------

def analyze_noise_patterns(image: Image.Image) -> dict[str, Any]:
    """Measure noise uniformity across image blocks.

    Real photographs have spatially varying noise (shadows are noisier,
    highlights are cleaner).  Synthetic images often have very uniform
    noise across the entire frame.

    Returns a dict with noise statistics and a uniformity score (0-1,
    where 1 = perfectly uniform = suspicious).
    """
    grey = image.convert("L")
    arr = np.asarray(grey, dtype=np.float64)

    if arr.size == 0:
        return {"block_stddevs": [], "noise_uniformity": 0.0, "mean_noise": 0.0}

    block_size = 64
    h, w = arr.shape
    stddevs: list[float] = []

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = arr[y : y + block_size, x : x + block_size]
            stddevs.append(float(np.std(block)))

    if not stddevs:
        # Image smaller than one block — just use overall stddev
        overall = float(np.std(arr))
        return {"block_stddevs": [overall], "noise_uniformity": 1.0, "mean_noise": overall}

    mean_std = float(np.mean(stddevs))
    std_of_stds = float(np.std(stddevs))

    # Uniformity: low variation across blocks → high uniformity → suspicious
    if mean_std == 0:
        uniformity = 1.0
    else:
        coefficient_of_variation = std_of_stds / mean_std
        # Map CV to 0-1 range; CV < 0.15 is very uniform
        uniformity = max(0.0, 1.0 - coefficient_of_variation / 0.5)
        uniformity = min(1.0, uniformity)

    return {
        "block_stddevs": stddevs[:20],  # first 20 for metadata (keep payload small)
        "noise_uniformity": round(uniformity, 4),
        "mean_noise": round(mean_std, 4),
    }


# ---------------------------------------------------------------------------
# PDF font analysis
# ---------------------------------------------------------------------------

def detect_inconsistent_fonts(pdf_bytes: bytes) -> dict[str, Any]:
    """Check fonts used across pages of a PDF.

    Returns information about fonts found and whether they appear
    inconsistent (which can indicate splicing or generation).
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    page_fonts: list[list[str]] = []

    for page in reader.pages:
        fonts: list[str] = []
        resources = page.get("/Resources")
        if resources:
            font_dict = resources.get("/Font")
            if font_dict:
                font_obj = font_dict.get_object() if hasattr(font_dict, "get_object") else font_dict
                if isinstance(font_obj, dict):
                    for key in font_obj:
                        font_ref = font_obj[key]
                        try:
                            font_info = font_ref.get_object() if hasattr(font_ref, "get_object") else font_ref
                            base_font = font_info.get("/BaseFont", "Unknown")
                            fonts.append(str(base_font))
                        except Exception:
                            fonts.append("Unknown")
        page_fonts.append(fonts)

    all_fonts = set()
    for pf in page_fonts:
        all_fonts.update(pf)

    # Heuristic: many different fonts across pages can be suspicious
    inconsistent = len(all_fonts) > 6

    return {
        "total_unique_fonts": len(all_fonts),
        "fonts": sorted(all_fonts),
        "page_count": len(reader.pages),
        "inconsistent": inconsistent,
    }


# ---------------------------------------------------------------------------
# Screenshot detection helpers
# ---------------------------------------------------------------------------

_SCREENSHOT_SOFTWARE = [
    "screenshot", "snipping", "snagit", "lightshot", "greenshot",
    "sharex", "gyazo", "flameshot", "spectacle", "grab", "scrot",
    "windows.photos", "preview",
]


def _is_screenshot_indicator(metadata: dict[str, Any]) -> bool:
    """Return True if metadata suggests the image is a screenshot."""
    software = str(metadata.get("Software", "")).lower()
    if any(kw in software for kw in _SCREENSHOT_SOFTWARE):
        return True
    # Common screenshot dimensions (exact monitor resolutions)
    width = metadata.get("ImageWidth") or metadata.get("ExifImageWidth")
    height = metadata.get("ImageLength") or metadata.get("ExifImageHeight")
    if width and height:
        common_resolutions = {
            (1920, 1080), (2560, 1440), (3840, 2160),
            (1366, 768), (1440, 900), (1536, 864),
            (2560, 1600), (2880, 1800), (3024, 1964),
        }
        if (int(width), int(height)) in common_resolutions:
            return True
    return False


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------

def _score_image(image: Image.Image) -> tuple[float, list[str], dict[str, Any]]:
    """Analyse an image and return (score_0_100, reasons, metadata)."""
    reasons: list[str] = []
    score = 0.0
    all_metadata: dict[str, Any] = {}

    # --- EXIF analysis ---
    exif = extract_exif_metadata(image)
    all_metadata["exif"] = exif

    if not exif:
        score += 25
        reasons.append("No EXIF metadata found (common in synthetic images)")
    else:
        # Check for camera-related fields that real photos usually have
        camera_fields = {"Make", "Model", "FocalLength", "ExposureTime", "ISOSpeedRatings"}
        present = camera_fields & set(exif.keys())
        if not present:
            score += 15
            reasons.append("EXIF present but missing camera fields (Make, Model, etc.)")

        if _is_screenshot_indicator(exif):
            score += 20
            reasons.append("Metadata indicates image is a screenshot")

    # --- DPI analysis ---
    dpi = image.info.get("dpi")
    all_metadata["dpi"] = dpi
    if dpi:
        x_dpi, y_dpi = dpi
        if x_dpi != y_dpi:
            score += 15
            reasons.append(f"Inconsistent DPI: x={x_dpi}, y={y_dpi}")
        if x_dpi == 72 and y_dpi == 72:
            score += 10
            reasons.append("DPI is exactly 72 (common default for generated images)")
    else:
        score += 5
        reasons.append("No DPI information found")

    # --- Noise analysis ---
    noise = analyze_noise_patterns(image)
    all_metadata["noise"] = {
        "uniformity": noise["noise_uniformity"],
        "mean_noise": noise["mean_noise"],
    }
    if noise["noise_uniformity"] > 0.85:
        score += 20
        reasons.append(
            f"Very uniform noise pattern (uniformity={noise['noise_uniformity']:.2f}); "
            "real photos typically have spatially varying noise"
        )
    elif noise["noise_uniformity"] > 0.7:
        score += 10
        reasons.append(f"Moderately uniform noise (uniformity={noise['noise_uniformity']:.2f})")

    if noise["mean_noise"] < 2.0 and image.size[0] > 100:
        score += 10
        reasons.append("Extremely low noise level — image may be computer-generated")

    # --- Image dimensions / format ---
    all_metadata["dimensions"] = {"width": image.width, "height": image.height}
    all_metadata["format"] = image.format

    # Check for exact monitor resolutions (screenshot indicator)
    common_resolutions = {
        (1920, 1080), (2560, 1440), (3840, 2160),
        (1366, 768), (1440, 900), (1536, 864),
    }
    if (image.width, image.height) in common_resolutions and not exif:
        score += 10
        reasons.append("Image dimensions match common screen resolution with no EXIF")

    score = min(score, 100.0)
    return score, reasons, all_metadata


def _score_pdf(pdf_bytes: bytes) -> tuple[float, list[str], dict[str, Any]]:
    """Analyse a PDF and return (score_0_100, reasons, metadata)."""
    reasons: list[str] = []
    score = 0.0
    all_metadata: dict[str, Any] = {}

    reader = PdfReader(io.BytesIO(pdf_bytes))
    all_metadata["page_count"] = len(reader.pages)

    # --- PDF metadata ---
    pdf_meta = reader.metadata
    if pdf_meta:
        meta_dict = {}
        for key in ["/Title", "/Author", "/Creator", "/Producer", "/CreationDate", "/ModDate"]:
            val = pdf_meta.get(key)
            if val:
                meta_dict[key.lstrip("/")] = str(val)
        all_metadata["pdf_metadata"] = meta_dict

        producer = str(pdf_meta.get("/Producer", "")).lower()
        creator = str(pdf_meta.get("/Creator", "")).lower()

        ai_tools = ["chatgpt", "dall-e", "midjourney", "stable diffusion", "jasper", "ai"]
        for tool in ai_tools:
            if tool in producer or tool in creator:
                score += 25
                reasons.append(f"PDF producer/creator mentions AI tool: '{tool}'")
                break
    else:
        score += 10
        reasons.append("No PDF metadata found")

    # --- Font analysis ---
    font_info = detect_inconsistent_fonts(pdf_bytes)
    all_metadata["fonts"] = font_info

    if font_info["inconsistent"]:
        score += 15
        reasons.append(
            f"Large number of unique fonts ({font_info['total_unique_fonts']}); "
            "may indicate document splicing"
        )

    if font_info["total_unique_fonts"] == 0 and len(reader.pages) > 0:
        score += 20
        reasons.append("No embedded fonts found — pages may be rasterized/generated images")

    # --- Text extraction analysis ---
    total_text = ""
    for page in reader.pages:
        total_text += page.extract_text() or ""

    word_count = len(total_text.split())
    all_metadata["word_count"] = word_count

    if word_count == 0 and len(reader.pages) > 0:
        score += 15
        reasons.append("PDF contains no extractable text (image-only PDF)")

    # --- Embedded image analysis (check first page) ---
    try:
        first_page = reader.pages[0]
        resources = first_page.get("/Resources")
        if resources:
            xobjects = resources.get("/XObject")
            if xobjects:
                xobj = xobjects.get_object() if hasattr(xobjects, "get_object") else xobjects
                image_count = 0
                if isinstance(xobj, dict):
                    for key in xobj:
                        obj = xobj[key]
                        try:
                            resolved = obj.get_object() if hasattr(obj, "get_object") else obj
                            if resolved.get("/Subtype") == "/Image":
                                image_count += 1
                        except Exception:
                            pass
                if image_count > 0 and word_count == 0:
                    score += 10
                    reasons.append(f"PDF has {image_count} embedded image(s) but no text")
    except Exception:
        pass

    score = min(score, 100.0)
    return score, reasons, all_metadata


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def detect_document(file_bytes: bytes, content_type: str) -> dict[str, Any]:
    """Analyse a document (image or PDF) for synthetic content indicators.

    Returns a dict conforming to the schema:
        {
            "is_synthetic": bool,
            "confidence": float (0-1),
            "reasons": [str, ...],
            "metadata": { ... }
        }
    """
    if content_type == "application/pdf":
        score, reasons, metadata = _score_pdf(file_bytes)
    else:
        # Assume image
        image = Image.open(io.BytesIO(file_bytes))
        score, reasons, metadata = _score_image(image)

    confidence = round(score / 100.0, 4)
    is_synthetic = confidence >= 0.5

    return {
        "is_synthetic": is_synthetic,
        "confidence": confidence,
        "reasons": reasons,
        "metadata": metadata,
    }
