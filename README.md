# Document Processing and Validation System

A practical document-processing application that turns invoice images into structured data. It combines OpenCV preprocessing, Tesseract OCR, rule-based extraction, validation, confidence scoring, SQLite persistence, and a FastAPI API with a browser interface.

## What it solves

Invoice data is often trapped inside images or scans. This system automates the first pass: clean the document, read its text, identify common invoice fields, check arithmetic rules, and clearly flag uncertain records for human review.

## Processing pipeline

`Upload → Preprocess → OCR → Extract fields → Validate → Confidence score → Store → Review`

## Features

- PNG/JPG/JPEG invoice upload with size validation
- OpenCV grayscale, resize, blur reduction and Otsu thresholding
- Tesseract OCR
- Extraction of invoice number, date, vendor, customer, currency, subtotal, tax/GST and total
- Arithmetic validation: `subtotal + tax = total`
- Missing-field checks
- Confidence score and automatic `MANUAL_REVIEW` status for low-confidence records
- SQLite persistence using SQLAlchemy
- FastAPI REST API with interactive Swagger documentation
- Responsive browser UI with drag-and-drop upload and progress feedback
- Docker support
- Automated unit tests for extraction and validation

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/documents/upload` | Upload a document |
| POST | `/documents/{id}/process` | Run OCR and extraction |
| GET | `/documents/{id}` | Read processing result |
| POST | `/documents/{id}/validate` | Re-run validation |

## Run locally

Install Tesseract OCR, then:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the application or `http://127.0.0.1:8000/docs` for Swagger.

Run tests:

```bash
pytest -q
```

## Run with Docker

```bash
docker compose up --build
```

Then open `http://127.0.0.1:8000`.

## Project structure

```text
app/
  main.py          # FastAPI routes and processing workflow
  services.py      # OpenCV, OCR, extraction, validation
  models.py        # SQLAlchemy document model
  db.py            # SQLite database setup
frontend/
  index.html       # Browser interface
  app.js           # Upload and result workflow
  style.css        # UI styling
tests/
  test_services.py # Unit tests
```

## Important limitation

OCR and extraction quality depends on the document image and layout. A confidence score is a routing signal, not a guarantee of correctness. Production use would require a larger evaluation dataset, stronger document classification, authentication, asynchronous jobs, and monitoring.

Never commit private documents, database files, API keys, or other sensitive data.
