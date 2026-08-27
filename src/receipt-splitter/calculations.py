from models import Receipt, Item, Person
from decimal import Decimal
from fractions import Fraction


def calculate_subtotal(receipt: Receipt) -> Decimal:
    """Calculate subtotal by summing prices of all items"""
    return sum(item.price for item in receipt.items)

def validate_subtotal(receipt: Receipt) -> bool:
    """Check whether receipt subtotal matches sum of item prices"""
    return receipt.subtotal == calculate_subtotal(receipt)

def split_item(item: Item) -> dict[str, Fraction]:
    """Calculate each person's exact fractional share of an item in cents"""
    if not item.shared_by:
        raise ValueError("No person attached to item")

    cents = int(item.price * 100)

    split = {}

    for person in item.shared_by:

        split[person.name] = Fraction(cents, len(item.shared_by))

    return split

def calculate_person_subtotal(receipt: Receipt) -> dict[str, int]:
    """Calculate and fairly round each person's share of receipt subtotal"""
    if not validate_subtotal(receipt):
        raise ValueError("Receipt subtotal doesn't match item prices")
    
    totals = {}
    for item in receipt.items:

        split = split_item(item)

        for name in split:
            if name in totals:
                totals[name] += split[name]
            else:
                totals[name] = split[name]

    return round_subtotal(totals, int(receipt.subtotal * 100))

def round_subtotal(totals: dict[str, Fraction], cents: int) -> dict[str, int]:
    """Round exact fractional cent subtotals while preserving receipt subtotal"""
    rounded_down = {}
    fractionals = {}
    for name in totals:
        rounded_down[name], fractionals[name] = divmod(totals[name], 1)

    if cents == sum(rounded_down.values()):
        return rounded_down

    remainder = cents - sum(rounded_down.values())
    fractionals = dict(sorted(fractionals.items(), key=lambda item: item[1], reverse=True))

    for name in fractionals:
        if not remainder:
            break
        rounded_down[name] += 1
        remainder -= 1

    return rounded_down