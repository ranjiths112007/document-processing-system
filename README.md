# Document Processing and Validation System

A Document Processing and Validation System Using Python, OpenCV, Tesseract OCR, FastAPI, SQLAlchemy, Docker. I built to understand how document automation works from end to end.

This application takes an invoice image, processes it with computer vision and OCR, extracts useful invoice fields, validates the extracted values, stores the result, and presents everything through a simple web interface and REST API.

The main goal of this project was not to build a flashy AI demo. I wanted to build something I could actually understand, run, test, explain, and improve.

---

## Why I built this

A lot of useful business information is still stored inside scanned documents, screenshots, and invoice images. Manually reading those documents and entering the same information into another system is repetitive and error-prone.

I built this project as a hands-on way to solve that problem while learning how different parts of an AI/software pipeline fit together:

- Image preprocessing
- Optical Character Recognition (OCR)
- Text extraction and parsing
- Data validation
- Confidence-based review
- REST API development
- Database persistence
- Frontend integration
- Dockerized execution
- Automated testing

The interesting part for me was connecting these pieces into one working application instead of treating them as separate tutorials.

---

## What the system does

The current version is focused on **invoice document processing**.

A user uploads an invoice image through the web interface. The backend then:

1. Accepts and stores the document.
2. Preprocesses the image using OpenCV.
3. Runs Tesseract OCR to convert the image into text.
4. Extracts common invoice fields from the OCR output.
5. Validates required fields and invoice totals.
6. Calculates a confidence score from the extraction results.
7. Flags lower-confidence results for manual review.
8. Saves the processing result in SQLite.
9. Returns the structured result through the API and displays it in the browser.

### Processing pipeline

```text
Invoice Image
     ↓
Upload
     ↓
OpenCV Preprocessing
     ↓
Tesseract OCR
     ↓
Text Extraction
     ↓
Invoice Field Extraction
     ↓
Validation
     ↓
Confidence Scoring
     ↓
SQLite Persistence
     ↓
FastAPI Response + Web UI
```

---

## What can be extracted

The system currently looks for common invoice information such as:

- Invoice number
- Invoice date
- Vendor / supplier
- Customer
- Currency
- Subtotal
- Tax / GST / VAT
- Total / grand total

It also performs basic consistency checks, including:

```text
Subtotal + Tax = Total
```

If important information is missing or the extracted values do not pass validation, the result can be flagged for manual review instead of being treated as automatically correct.

---

## Technical implementation

### 1. Image processing — OpenCV

Before OCR, the uploaded image goes through a preprocessing step designed to make the text easier for the OCR engine to read.

The current pipeline includes:

- Grayscale conversion
- Image resizing when required
- Gaussian blur for noise reduction
- Otsu thresholding

This gave me a practical understanding of why OCR quality depends heavily on the quality and preparation of the input image.

### 2. OCR — Tesseract

Tesseract OCR is used to convert the processed document image into machine-readable text.

The OCR output is intentionally kept available in the result so that the extracted fields can be compared with the original recognized text during debugging and review.

### 3. Information extraction

The current extraction layer uses Python-based text parsing and regular expressions to identify common invoice fields.

I chose a rule-based approach for this version because it is simple, explainable, and easy to test. It also makes the limitations of the system visible rather than hiding them behind a black-box model.

### 4. Validation

Extracted data is checked before being considered usable.

Examples include:

- Required field checks
- Numeric value checks
- Invoice total consistency
- Validation issue reporting

### 5. Confidence scoring

The application produces a confidence score based on the quality and completeness of the extracted information.

The score is used as a **review signal**, not as a claim that the OCR is always correct. Lower-confidence documents can be routed to `MANUAL_REVIEW`.

### 6. Backend — FastAPI

FastAPI provides the REST API and connects the upload, processing, validation, and persistence layers.

Interactive API documentation is also available through Swagger UI.

### 7. Database — SQLite + SQLAlchemy

Processed documents and their results are persisted using SQLite through SQLAlchemy.

This keeps the project lightweight and easy to run locally while still demonstrating the basic persistence layer used in a real application.

### 8. Frontend

The project includes a responsive browser interface with:

- Drag-and-drop upload
- File selection
- Processing progress
- Extracted field display
- Confidence score
- Validation results
- Raw OCR output

The frontend communicates with the FastAPI backend rather than containing the processing logic itself.

### 9. Docker

The application can also be run using Docker, with the required Tesseract system dependency installed inside the container.

### 10. Testing

Unit tests cover important parts of the extraction and validation logic, including:

- Invoice field extraction
- Valid invoice totals
- Incorrect totals
- Missing required fields

GitHub Actions is configured to run the test suite on repository changes.

---

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check service health |
| `POST` | `/documents/upload` | Upload a document |
| `POST` | `/documents/{id}/process` | Process the uploaded document |
| `GET` | `/documents/{id}` | Get the processing result |
| `POST` | `/documents/{id}/validate` | Re-run validation |

FastAPI's interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Project structure

```text
document-processing-system/
│
├── app/
│   ├── main.py          # FastAPI routes and application workflow
│   ├── services.py      # OpenCV, OCR, extraction and validation logic
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # API data schemas
│   └── db.py            # SQLite database configuration
│
├── frontend/
│   ├── index.html       # Web interface
│   ├── app.js           # Upload and API interaction logic
│   └── style.css        # Frontend styling
│
├── tests/
│   └── test_services.py # Unit tests
│
├── .github/
│   └── workflows/
│       └── tests.yml    # Automated test workflow
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Running the project locally

### Prerequisites

You need:

- Python 3.11+
- Tesseract OCR
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ranjiths112007/document-processing-system.git
cd document-processing-system
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

or the API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Run the tests

```bash
pytest -q
```

---

## Running with Docker

If Docker is installed, the complete application can be started with:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000
```

---

## Example workflow

A typical use of the application looks like this:

```text
1. Upload invoice image
        ↓
2. Image is preprocessed
        ↓
3. OCR reads the document
        ↓
4. Invoice fields are extracted
        ↓
5. Values are validated
        ↓
6. Confidence is calculated
        ↓
7. Result is saved
        ↓
8. User reviews structured output
```

This makes the project useful as a small foundation for automated invoice processing rather than just an OCR demo.

---

## What I learned from building it

Building this project helped me understand several things that are easy to miss when learning individual technologies separately.

### Computer vision is part of the AI pipeline

OCR quality is not only about the OCR engine. Image quality, scaling, noise, and thresholding can have a major effect on the text that eventually gets extracted.

### Extracted text is not automatically reliable data

OCR produces text, but an application still needs to interpret and validate that text before using it as structured information.

### APIs make AI components usable

The OCR and extraction logic becomes much more useful when it is exposed through a clean API that a frontend or another application can consume.

### Validation matters

A system should not blindly trust extracted information. Basic business rules can catch obvious inconsistencies and identify cases that need human review.

### Simple and explainable can be better

For this version, I deliberately used rule-based extraction instead of adding an unnecessary machine-learning or LLM layer. That keeps the system understandable and makes it easier for me to explain exactly how every part works.

---

## Current scope and limitations

This is a **working learning/project implementation**, not a production-grade enterprise document platform.

The current version is mainly designed around invoice images with reasonably clear layouts. OCR and rule-based extraction can fail when documents contain unusual layouts, poor image quality, handwriting, complex tables, or unexpected field formats.

The confidence score should therefore be treated as a routing signal rather than a guarantee of accuracy.

For a production system, I would consider adding:

- Support for more document types
- PDF and multi-page document processing
- Stronger document classification
- More robust field extraction
- OCR confidence at token/field level
- A larger evaluation dataset
- Authentication and authorization
- Asynchronous/background processing
- Better observability and monitoring
- PostgreSQL or another production database
- LLM-assisted extraction where it provides measurable value

These are future improvements, not claims about the current implementation.

---

## Project focus

This project sits mainly at the intersection of:

**Python + Computer Vision + OCR + FastAPI + REST APIs + Document Automation**

It also gives me practical exposure to software engineering concepts such as database persistence, testing, Docker, API design, frontend/backend integration, and validation.

---

## Author

**Ranjith**

I built this project as a hands-on learning project to strengthen my understanding of Python-based AI applications, computer vision, OCR, backend APIs, and end-to-end application development.

The repository is intentionally kept practical and explainable so that I can understand the implementation rather than simply present a collection of tools.

---

## Repository

GitHub: https://github.com/ranjiths112007/document-processing-system

If you find the project useful or have ideas for improving the document-processing pipeline, feel free to explore the repository and share feedback.

---

## Responsible use

Do not commit private invoices, financial records, personal documents, API keys, database files, or other sensitive information to the repository.

Use synthetic or sanitized documents when testing and demonstrating the project.
