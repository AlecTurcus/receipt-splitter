from fastapi.testclient import TestClient
from receipt_splitter.api import app
import receipt_splitter.api as api_module
from receipt_splitter.models import ExtractedReceipt, ExtractedItem

client = TestClient(app)


def test_calculate_receipt_endpoint():
    receipt = {
        "items": [
            {
                "name": "Burger",
                "price": "20.00",
                "shared_by": [
                    {"name": "Alice"}
                ]
            },
            {
                "name": "Pasta",
                "price": "30.00",
                "shared_by": [
                    {"name": "Bob"}
                ]
            }
        ],
        "subtotal": "50.00",
        "tax": "5.00",
        "tip": "10.00",
        "total": "65.00",
        "people": [
            {"name": "Alice"},
            {"name": "Bob"}
        ]
    }

    response = client.post("/receipts/calculate", json = receipt)

    assert response.status_code == 200

    assert response.json() == {
        "Alice": 26.0,
        "Bob": 39.0
    }

def test_calculate_receipt_invalid_endpoint():
    receipt = {
        "items": [
            {
                "name": "Burger",
                "price": "20.00",
                "shared_by": [
                    {"name": "Alice"}
                ]
            },
            {
                "name": "Pasta",
                "price": "30.00",
                "shared_by": [
                    {"name": "Bob"}
                ]
            }
        ],
        "subtotal": "60.00",
        "tax": "5.00",
        "tip": "10.00",
        "total": "65.00",
        "people": [
            {"name": "Alice"},
            {"name": "Bob"}
        ]
    }

    response = client.post("/receipts/calculate", json = receipt)

    assert response.status_code == 400

def test_extract_receipt_invalid_file_type():
    response = client.post(
        "/receipts/extract",
        files={
            "file": ("notes.txt", b"not an image", "text/plain")
        }
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": "Unsupported file type"
    }

def test_extract_receipt_success(monkeypatch):
    def fake_extract_receipt(image_bytes, mime_type):
        return ExtractedReceipt(
            items=[
                ExtractedItem(name="Burger", line_total="10.00", unit_price = "10.00")
            ],
            subtotal="10.00",
            tax="1.00",
            tip="0.00",
            total="11.00"
        )

    monkeypatch.setattr(api_module, "extract_receipt", fake_extract_receipt)

    response = client.post(
            "/receipts/extract",
            files={
                "file": ("receipt.jpg", b"receipt image", "image/jpg")
            }
        )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "name": "Burger",
                "price": "10.00",
                "quantity": 1,
                "shared_by": []
            }
        ],
        "subtotal": "10.00",
        "tax": "1.00",
        "tip": "0.00",
        "total": "11.00",
        "people": []
}
    