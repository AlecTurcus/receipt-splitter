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
    
    subtotals = {}
    for item in receipt.items:

        split = split_item(item)

        for name in split:
            if name in subtotals:
                subtotals[name] += split[name]
            else:
                subtotals[name] = split[name]

    return allocate_cents(subtotals, int(receipt.subtotal * 100))

def allocate_cents(subtotals: dict[str, Fraction], cents: int) -> dict[str, int]:
    """Convert fractional cent allocations into whole cents while preserving total"""
    allocated = {}
    fractionals = {}
    for name in subtotals:
        allocated[name], fractionals[name] = divmod(subtotals[name], 1)

    if cents == sum(allocated.values()):
        return allocated

    remainder = cents - sum(allocated.values())
    fractionals = dict(sorted(fractionals.items(), key=lambda item: item[1], reverse=True))

    for name in fractionals:
        if not remainder:
            break
        allocated[name] += 1
        remainder -= 1

    return allocated

def calculate_person_tax(receipt: Receipt, subtotals: dict[str, int]) -> dict[str, int]:
    if receipt.tax == 0:
        return {name: 0 for name in subtotals}
    tax_allocations = {}
    subtotal_cents = int(receipt.subtotal * 100)
    tax_cents = int(receipt.tax * 100)

    if subtotal_cents == 0:
        raise ValueError("Zero subtotal")

    for name in subtotals:
        tax_allocations[name] = (Fraction(subtotals[name], subtotal_cents) * tax_cents)

    
    return allocate_cents(tax_allocations, tax_cents)