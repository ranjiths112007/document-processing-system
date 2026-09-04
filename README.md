# Document Processing and Validation System

A practical document-processing application that accepts invoice images, improves image quality with OpenCV, extracts text with Tesseract OCR, converts common invoice fields into structured data, validates business rules, stores results in SQLite, and exposes the workflow through a FastAPI REST API.

## Problem

Manual document processing is repetitive and error-prone. The system automates the first stage of turning image-based invoices into structured information that can be reviewed by a human.

## Current MVP

- PNG/JPG/JPEG document upload
- File type and size validation
- OpenCV preprocessing (grayscale, resize, blur reduction, Otsu thresholding)
- Tesseract OCR
- Regex-based invoice field extraction
- Invoice arithmetic validation (`subtotal + tax = total`)
- Confidence score and manual-review status
- SQLite persistence
- FastAPI REST endpoints and Swagger documentation
- Simple browser UI
- Docker and Docker Compose

## Processing Flow

`Upload -> OpenCV preprocessing -> Tesseract OCR -> field extraction -> validation -> confidence score -> SQLite -> REST API / web UI`

## API

- `GET /health`
- `POST /documents/upload`
- `POST /documents/{document_id}/process`
- `GET /documents/{document_id}`
- `POST /documents/{document_id}/validate`

## Run locally

Install Tesseract OCR on your machine, then:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the UI or `http://127.0.0.1:8000/docs` for Swagger.

## Run with Docker

```bash
docker compose up --build
```

## Notes

The MVP intentionally uses deterministic extraction before adding an LLM layer. This makes failures easier to debug and means an API key is not required for the core pipeline.

Use synthetic or public sample documents only. Do not commit private identity documents, bank statements, uploaded files, databases, or API keys.

## Next steps

- PDF-to-image support
- LLM-assisted normalization and validation
- Better OCR confidence handling
- Automated tests and evaluation dataset
- Authentication
- Asynchronous processing
- Cloud deployment
