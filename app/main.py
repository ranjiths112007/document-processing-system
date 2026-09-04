import json
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Document
from .services import confidence_score, extract_invoice_fields, extract_text, preprocess_image, serialize_result, validate_invoice

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Document Processing and Validation System", version="1.0.0")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), document_type: str = "invoice", db: Session = Depends(get_db)):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PNG, JPG and JPEG files are supported in the MVP")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large")

    document_id = str(uuid4())
    path = UPLOAD_DIR / f"{document_id}{extension}"
    path.write_bytes(content)
    document = Document(id=document_id, filename=file.filename or "document", document_type=document_type, status="UPLOADED")
    db.add(document)
    db.commit()
    return {"document_id": document_id, "status": "UPLOADED"}


@app.post("/documents/{document_id}/process")
def process_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    source_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))
    if not source_files:
        document.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    try:
        document.status = "PROCESSING"
        db.commit()
        processed_path = OUTPUT_DIR / f"{document_id}_processed.png"
        preprocess_image(source_files[0], processed_path)
        raw_text = extract_text(processed_path)
        fields = extract_invoice_fields(raw_text) if document.document_type.lower() == "invoice" else {"raw_text": raw_text}
        validation = validate_invoice(fields) if document.document_type.lower() == "invoice" else {"validation_issues": []}
        confidence = confidence_score(fields, validation) if document.document_type.lower() == "invoice" else 0.0
        extracted_json, validation_json = serialize_result(fields, validation)

        document.raw_text = raw_text
        document.extracted_json = extracted_json
        document.validation_json = validation_json
        document.confidence = confidence
        document.status = "MANUAL_REVIEW" if confidence < 0.70 else "COMPLETED"
        db.commit()
        return {"document_id": document_id, "status": document.status}
    except Exception as exc:
        document.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")


@app.get("/documents/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,
        "fields": json.loads(document.extracted_json) if document.extracted_json else {},
        "validation": json.loads(document.validation_json) if document.validation_json else {},
        "confidence": document.confidence,
        "raw_text": document.raw_text,
    }


@app.post("/documents/{document_id}/validate")
def validate_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document or not document.extracted_json:
        raise HTTPException(status_code=404, detail="Processed document not found")
    fields = json.loads(document.extracted_json)
    validation = validate_invoice(fields)
    document.validation_json = json.dumps(validation)
    document.confidence = confidence_score(fields, validation)
    document.status = "MANUAL_REVIEW" if document.confidence < 0.70 else "COMPLETED"
    db.commit()
    return validation
