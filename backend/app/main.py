from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import detection

app = FastAPI(
    title="AI Content Detection API",
    description="API for detecting AI-generated content in text, images, audio, and PDFs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(detection.router, prefix="/api/v1")
