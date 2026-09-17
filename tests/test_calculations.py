from receipt_splitter.models import Receipt, Item, Person
from receipt_splitter.calculations import calculate_bill, split_item, calculate_subtotal

from decimal import Decimal
from fractions import Fraction

import pytest


def test_basic_bill():
    alice = Person(name="Alice")
    bob = Person(name="Bob")

    item1 = Item(name="Pizza", price="20.00", shared_by=[alice])
    item2 = Item(name="izza", price="30.00", shared_by=[bob])

    receipt = Receipt(
        items=[item1, item2],
        subtotal="50.00",
        tax="5.00",
        tip="10.00",
        total="65.00",
        people=[alice, bob]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("26.00"),
        "Bob": Decimal("39.00")
    }


def test_even_split():
    alice = Person(name="Alice")
    bob = Person(name="Bob")

    item1 = Item(name="Pizza", price="20.00", shared_by=[alice, bob])

    receipt = Receipt(
        items=[item1],
        subtotal="20.00",
        tax="0",
        tip="0",
        total="20",
        people=[alice, bob]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("10.00"),
        "Bob": Decimal("10.00")
    }


def test_share_remainder():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="Pizza", price="20.00", shared_by=[alice, bob, job])

    receipt = Receipt(
        items=[item1],
        subtotal="20.00",
        tax="0",
        tip="0",
        total="20.00",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert sum(result.values()) == Decimal("20")


def test_share_remainder_fairness():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="Pizza", price="20.00", shared_by=[alice, bob, job])
    item2 = Item(name="Pizza", price="0.03", shared_by=[alice, job])

    receipt = Receipt(
        items=[item1, item2],
        subtotal="20.03",
        tax="0",
        tip="0",
        total="20.03",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("6.68"),
        "Bob": Decimal("6.67"),
        "Job": Decimal("6.68")
    }


def test_tax_allocation():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])
    item3 = Item(name="Pizza", price="10.00", shared_by=[job])

    receipt = Receipt(
        items=[item1, item2, item3],
        subtotal="50.00",
        tax="3",
        tip="0",
        total="53",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("24.38"),
        "Bob": Decimal("18.02"),
        "Job": Decimal("10.60")
    }


def test_tip_allocation():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])
    item3 = Item(name="Pizza", price="10.00", shared_by=[job])

    receipt = Receipt(
        items=[item1, item2, item3],
        subtotal="50.00",
        tax="0",
        tip="3",
        total="53",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("24.38"),
        "Bob": Decimal("18.02"),
        "Job": Decimal("10.60")
    }


def test_tip_tax():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])
    item3 = Item(name="Pizza", price="10.00", shared_by=[job])

    receipt = Receipt(
        items=[item1, item2, item3],
        subtotal="50.00",
        tax="3",
        tip="3",
        total="56",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("25.76"),
        "Bob": Decimal("19.04"),
        "Job": Decimal("11.20")
    }


def test_person_no_item():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])

    receipt = Receipt(
        items=[item1, item2],
        subtotal="40.00",
        tax="0",
        tip="0",
        total="40",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("23"),
        "Bob": Decimal("17"),
        "Job": Decimal("0.00")
    }


def test_empty_shared_by():
    item1 = Item(name="izza", price="23.00", shared_by=[])

    with pytest.raises(ValueError, match="No person attached to item"):
        split_item(item1)


def test_invalid_receipt_subtotal():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])

    receipt = Receipt(
        items=[item1, item2],
        subtotal="30.00",
        tax="0",
        tip="0",
        total="40",
        people=[alice, bob, job]
    )

    with pytest.raises(ValueError, match="Receipt subtotal does not match summed item subtotal"):
        calculate_bill(receipt)


def test_invalid_total():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="23.00", shared_by=[alice])
    item2 = Item(name="Pzza", price="17.00", shared_by=[bob])

    receipt = Receipt(
        items=[item1, item2],
        subtotal="40.00",
        tax="0",
        tip="0",
        total="30",
        people=[alice, bob, job]
    )

    with pytest.raises(ValueError, match="Split total does not match receipt total"):
        calculate_bill(receipt)


def test_tip_tax_zero_subtotal():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="0", shared_by=[alice])
    item2 = Item(name="Pzza", price="0", shared_by=[bob])
    item3 = Item(name="Pizza", price="0", shared_by=[job])

    receipt = Receipt(
        items=[item1, item2, item3],
        subtotal="0",
        tax="3",
        tip="3",
        total="6",
        people=[alice, bob, job]
    )

    with pytest.raises(ValueError, match="Zero subtotal"):
        calculate_bill(receipt)


def test_one_person():
    alice = Person(name="Alice")

    item1 = Item(name="izza", price="10", shared_by=[alice])
    item2 = Item(name="Pzza", price="0.33", shared_by=[alice])
    item3 = Item(name="Pizza", price="11", shared_by=[alice])

    receipt = Receipt(
        items=[item1, item2, item3],
        subtotal="21.33",
        tax="3",
        tip="3",
        total="27.33",
        people=[alice]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("27.33")
    }


def test_big_bill():
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    job = Person(name="Job")

    item1 = Item(name="izza", price="20", shared_by=[alice, bob])
    item2 = Item(name="Pzza", price="17", shared_by=[bob])
    item3 = Item(name="Pizza", price="9.00", shared_by=[alice, job])
    item4 = Item(name="Pizza", price="13.00", shared_by=[alice, bob, job])
    item5 = Item(name="Pizza", price="8.00", shared_by=[job])

    receipt = Receipt(
        items=[item1, item2, item3, item4, item5],
        subtotal="67.00",
        tax="4.01",
        tip="6.03",
        total="77.04",
        people=[alice, bob, job]
    )

    result = calculate_bill(receipt)

    assert result == {
        "Alice": Decimal("21.67"),
        "Bob": Decimal("36.02"),
        "Job": Decimal("19.35")
    }


def test_quantity_effects_subtotal():
    item = Item(name="A", price="20.00", quantity=3)

    receipt = Receipt(
        items=[item],
        subtotal="60.00",
        tax="0.00",
        tip="0.00",
        total="60.00"
    )

    assert calculate_subtotal(receipt) == Decimal("60.00")


def test_quantity_effects_item_split():
    alice = Person(name="Alice")
    bob = Person(name="Bob")

    item = Item(name="A", price="20.00", quantity=3, shared_by=[alice, bob])

    result = split_item(item)

    assert result["Alice"] == Fraction(3000, 1)
    assert result["Bob"] == Fraction(3000, 1)