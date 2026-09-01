from receipt_splitter.extraction import parse_money, extracted_to_receipt
from receipt_splitter.models import ExtractedItem, ExtractedReceipt, Item, Receipt
from decimal import Decimal

def test_parse_money_valid():
    assert parse_money("39.00") == Decimal("39.00")

def test_parse_money_invalid():
    assert parse_money("a") == Decimal("0.00")

def test_extracted_to_receipt_valid():
    extracted = ExtractedReceipt(
        items = [
            ExtractedItem(name = "Item1", price = "39.00"),
            ExtractedItem(name = "Item2",  price = "0.01")
        ],
        subtotal = "39.01",
        tax = "4.00",
        tip = "0.00",
        total = "43.01"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt == Receipt(
        items = [
            Item(name = "Item1", price = Decimal("39.00")),
            Item(name = "Item2", price = Decimal("0.01"))
        ],
        subtotal = Decimal("39.01"),
        tax = Decimal("4.00"),
        tip = Decimal("0.00"),
        total = Decimal("43.01")
    )

def test_extracted_to_receipt_invalid():
    extracted = ExtractedReceipt(
        items = [
            ExtractedItem(name = "Item1", price = "39.00"),
            ExtractedItem(name = "Item2",  price = "null")
        ],
        subtotal = "39.01",
        tax = "4.00",
        tip = "null",
        total = "43.01"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt == Receipt(
        items = [
            Item(name = "Item1", price = Decimal("39.00")),
            Item(name = "Item2", price = Decimal("0.00"))
        ],
        subtotal = Decimal("39.01"),
        tax = Decimal("4.00"),
        tip = Decimal("0.00"),
        total = Decimal("43.01")
    )