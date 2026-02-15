from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.detector import detect_text, detect_image, detect_audio, detect_pdf

router = APIRouter(tags=["detection"])


@router.post("/detect/text")
async def analyze_text(payload: dict):
    """Analyze text content for AI generation indicators."""
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")
    result = await detect_text(text)
    return result


@router.post("/detect/image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze an uploaded image for AI generation indicators."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    contents = await file.read()
    result = await detect_image(contents)
    return result


@router.post("/detect/audio")
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze an uploaded audio file for AI generation indicators."""
    contents = await file.read()
    result = await detect_audio(contents)
    return result


@router.post("/detect/pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    """Analyze an uploaded PDF for AI-generated content."""
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    contents = await file.read()
    result = await detect_pdf(contents)
    return result
