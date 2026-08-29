from .models import Receipt, Item, Person
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
    
    subtotals = {person.name: 0 for person in receipt.people}
    for item in receipt.items:

        split = split_item(item)

        for name in split:
            if name in subtotals:
                subtotals[name] += split[name]
            else:
                subtotals[name] = split[name]

    return allocate_cents(subtotals, int(receipt.subtotal * 100))

def allocate_cents(allocations: dict[str, Fraction], total_cents: int) -> dict[str, int]:
    """Convert fractional cent allocations into whole cents while preserving total"""
    allocated = {}
    fractionals = {}
    for name in allocations:
        allocated[name], fractionals[name] = divmod(allocations[name], 1)

    if total_cents == sum(allocated.values()):
        return allocated

    remainder = total_cents - sum(allocated.values())
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

def calculate_person_tip(receipt: Receipt, subtotals: dict[str, int]) -> dict[str, int]:
    if receipt.tip == 0:
        return {name: 0 for name in subtotals}
    
    tip_allocations = {}
    subtotal_cents = int(receipt.subtotal * 100)
    tip_cents = int(receipt.tip * 100)

    if subtotal_cents == 0:
        raise ValueError("Zero subtotal")

    for name in subtotals:
        tip_allocations[name] = (Fraction(subtotals[name], subtotal_cents) * tip_cents)

    
    return allocate_cents(tip_allocations, tip_cents)


def calculate_final_totals(subtotals: dict[str, int], tax_allocations: dict[str, int], tip_allocations: dict[str, int]) -> dict[str, Decimal]:
    totals = {}
    for name in subtotals:
        totals[name] = Decimal(subtotals[name] + tax_allocations[name] + tip_allocations[name]) / Decimal("100")

    return totals

def calculate_bill(receipt: Receipt) -> dict[str, Decimal]:

    if not validate_subtotal(receipt):
        raise ValueError("Receipt subtotal does not match summed item subtotal")

    subtotals = calculate_person_subtotal(receipt)
    tax_allocations = calculate_person_tax(receipt, subtotals)
    tip_allocations = calculate_person_tip(receipt, subtotals)
    final_split = calculate_final_totals(subtotals, tax_allocations, tip_allocations)

    if sum(final_split.values()) != receipt.total:
        raise ValueError("Split total does not match receipt total")

    return final_split