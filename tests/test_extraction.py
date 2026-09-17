from receipt_splitter.extraction import parse_money, extracted_to_receipt
from receipt_splitter.models import ExtractedItem, ExtractedReceipt, Item, Receipt

from decimal import Decimal
from pydantic import ValidationError

import pytest


def test_parse_money_valid():
    assert parse_money("39.00") == Decimal("39.00")


def test_parse_money_invalid():
    assert parse_money("a") == Decimal("0.00")


def test_extracted_to_receipt_valid():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="Item1",
                unit_price="39.00",
                line_total="39.00"
            ),
            ExtractedItem(
                name="Item2", 
                unit_price="0.01", 
                line_total="0.01"
            )
        ],
        subtotal="39.01",
        tax="4.00",
        tip="0.00",
        total="43.01"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt == Receipt(
        items=[
            Item(
                name="Item1", 
                price=Decimal("39.00")
            ),
            Item(
                name="Item2", 
                price=Decimal("0.01")
            )
        ],
        subtotal=Decimal("39.01"),
        tax=Decimal("4.00"),
        tip=Decimal("0.00"),
        total=Decimal("43.01")
    )


def test_extracted_to_receipt_invalid():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="Item1", 
                line_total="39.00", 
                unit_price="39.00"
            ),
            ExtractedItem(
                name="Item2", 
                line_total="null", 
                unit_price="0.00"
            )
        ],
        subtotal="39.01",
        tax="4.00",
        tip="null",
        total="43.01"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt == Receipt(
        items=[
            Item(
                name="Item1", 
                price=Decimal("39.00")
            ),
            Item(
                name="Item2", 
                price=Decimal("0.00")
            )
        ],
        subtotal=Decimal("39.01"),
        tax=Decimal("4.00"),
        tip=Decimal("0.00"),
        total=Decimal("43.01")
    )


def test_quantity_defaults_to_one():
    item = Item(name="A", price="0")

    assert item.quantity == 1


def test_quantity_zero_invalid():
    with pytest.raises(ValidationError):
        Item(
            name="",
            price="0",
            quantity=0
        )


def test_extracted_quantity_converts_line_total_to_unit_price():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="",
                unit_price="0.00",
                line_total="30.00",
                quantity=3
            )
        ],
        subtotal="30.00",
        tax="0.00",
        tip="0.00",
        total="30.00"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt.items[0].price == Decimal("10.00")
    assert receipt.items[0].quantity == 3


def test_uses_line_total_when_present():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="Burger",
                quantity=2,
                unit_price="0.00",
                line_total="20.00"
            )
        ],
        subtotal="20.00",
        tax="0.00",
        tip="0.00",
        total="20.00"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt.items[0].price == Decimal("10.00")
    assert receipt.items[0].quantity == 2


def test_uses_unit_price_when_line_total_missing():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="Burger",
                quantity=2,
                unit_price="10.00",
                line_total="0.00"
            )
        ],
        subtotal="20.00",
        tax="0.00",
        tip="0.00",
        total="20.00"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt.items[0].price == Decimal("10.00")
    assert receipt.items[0].quantity == 2


def test_line_total_takes_priority_over_unit_price():
    extracted = ExtractedReceipt(
        items=[
            ExtractedItem(
                name="Burger",
                quantity=2,
                unit_price="9.00",
                line_total="20.00"
            )
        ],
        subtotal="20.00",
        tax="0.00",
        tip="0.00",
        total="20.00"
    )

    receipt = extracted_to_receipt(extracted)

    assert receipt.items[0].price == Decimal("10.00")