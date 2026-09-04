import json
import re
from pathlib import Path

import cv2
import numpy as np
import pytesseract


def preprocess_image(input_path: Path, output_path: Path) -> Path:
    image = cv2.imread(str(input_path))
    if image is None:
        raise ValueError("Unable to read image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale = 1600 / max(gray.shape)
    if scale > 1:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), processed)
    return output_path


def extract_text(image_path: Path) -> str:
    text = pytesseract.image_to_string(str(image_path))
    return text.strip()


def _first(pattern: str, text: str):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_invoice_fields(text: str) -> dict:
    fields = {
        "invoice_number": _first(r"invoice\s*(?:no|number|#)\s*[:\-]?\s*([A-Z0-9\-/]+)", text),
        "invoice_date": _first(r"(?:invoice\s*)?date\s*[:\-]?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})", text),
        "vendor_name": _first(r"vendor\s*(?:name)?\s*[:\-]?\s*(.+)", text),
        "customer_name": _first(r"customer\s*(?:name)?\s*[:\-]?\s*(.+)", text),
        "currency": _first(r"\b(USD|INR|EUR|GBP)\b", text),
    }
    for key, label in [("subtotal", "subtotal"), ("tax", "tax"), ("total_amount", "total")]:
        value = _first(rf"{label}\s*[:\-]?\s*(?:₹|INR|Rs\.?|\$|USD)?\s*([0-9,]+(?:\.\d+)?)", text)
        fields[key] = float(value.replace(",", "")) if value else None
    return fields


def validate_invoice(fields: dict) -> dict:
    issues = []
    subtotal = fields.get("subtotal")
    tax = fields.get("tax")
    total = fields.get("total_amount")
    amount_check = "NOT_CHECKED"
    if subtotal is not None and tax is not None and total is not None:
        amount_check = "PASS" if abs((subtotal + tax) - total) < 0.01 else "FAIL"
        if amount_check == "FAIL":
            issues.append("subtotal + tax does not equal total")
    for required in ("invoice_number", "invoice_date", "total_amount"):
        if fields.get(required) is None:
            issues.append(f"missing {required}")
    return {"amount_validation": amount_check, "validation_issues": issues}


def confidence_score(fields: dict, validation: dict) -> float:
    populated = sum(v is not None for v in fields.values())
    extraction = populated / max(len(fields), 1)
    validation_score = 1.0 if not validation["validation_issues"] else max(0.0, 1 - 0.2 * len(validation["validation_issues"]))
    return round(0.7 * extraction + 0.3 * validation_score, 2)


def serialize_result(fields: dict, validation: dict) -> tuple[str, str]:
    return json.dumps(fields, default=str), json.dumps(validation)
