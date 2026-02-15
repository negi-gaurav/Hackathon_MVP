# AI Content Detection API

Detect AI-generated content across text, images, audio, and PDFs.

## Project Structure

```
Hackathon_MVP/
├── backend/          # FastAPI application
│   └── app/
│       ├── main.py           # App entrypoint
│       ├── config.py         # Settings
│       ├── routers/          # API route handlers
│       │   └── detection.py
│       ├── services/         # Business logic
│       │   └── detector.py
│       └── utils/
├── frontend/         # React application
├── models/           # ML model files
├── test_data/        # Sample files for testing
├── docs/             # Documentation
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Setup

### Local Development

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### Docker

```bash
docker compose up --build
```

## API Endpoints

| Method | Path               | Description                |
|--------|--------------------| --------------------------|
| GET    | /health            | Health check               |
| POST   | /api/v1/detect/text  | Analyze text content       |
| POST   | /api/v1/detect/image | Analyze an uploaded image  |
| POST   | /api/v1/detect/audio | Analyze an uploaded audio file |
| POST   | /api/v1/detect/pdf   | Analyze an uploaded PDF    |

### Example: Text Detection

```bash
curl -X POST http://localhost:8000/api/v1/detect/text \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
```
