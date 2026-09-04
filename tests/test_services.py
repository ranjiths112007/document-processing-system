from app.services import confidence_score, extract_invoice_fields, validate_invoice


def test_extract_invoice_fields():
    text = """INVOICE\nInvoice No: INV-1042\nDate: 04/09/2026\nVendor Name: Example Technologies\nCustomer Name: Acme Ltd\nCurrency: INR\nSubtotal: INR 1000.00\nGST: INR 180.00\nGrand Total: INR 1180.00"""
    fields = extract_invoice_fields(text)
    assert fields["invoice_number"] == "INV-1042"
    assert fields["invoice_date"] == "04/09/2026"
    assert fields["subtotal"] == 1000.0
    assert fields["tax"] == 180.0
    assert fields["total_amount"] == 1180.0


def test_validation_passes_for_consistent_invoice():
    fields = {"invoice_number":"INV-1","invoice_date":"04/09/2026","vendor_name":"A","customer_name":"B","currency":"INR","subtotal":1000.0,"tax":180.0,"total_amount":1180.0}
    validation = validate_invoice(fields)
    assert validation["amount_validation"] == "PASS"
    assert validation["validation_issues"] == []
    assert confidence_score(fields, validation) == 1.0


def test_validation_flags_bad_total():
    fields = {"invoice_number":"INV-1","invoice_date":"04/09/2026","vendor_name":"A","customer_name":"B","currency":"INR","subtotal":1000.0,"tax":180.0,"total_amount":1200.0}
    validation = validate_invoice(fields)
    assert validation["amount_validation"] == "FAIL"
    assert "subtotal + tax does not equal total" in validation["validation_issues"]


def test_validation_flags_missing_required_fields():
    validation = validate_invoice({"invoice_number":None,"invoice_date":None,"total_amount":None})
    assert len(validation["validation_issues"]) == 3
