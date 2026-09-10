from .models import Receipt, Item, Person
from decimal import Decimal
from fractions import Fraction


def calculate_subtotal(receipt: Receipt) -> Decimal:
    """Calculate subtotal by summing prices of all items
    
    Args: 
        receipt (Receipt): Receipt containing items to total

    Returns:
        Decimal: Calculated subtotal of items in receipt
    """
    return sum(item.price * item.quantity for item in receipt.items)

def validate_subtotal(receipt: Receipt) -> bool:
    """Check whether receipt subtotal matches sum of item prices
    
    Args: 
        receipt (Receipt): Receipt containing subtotal

    Returns:
        bool: True if subtotal of items equals subtotal listed in receipt object
    """
    return receipt.subtotal == calculate_subtotal(receipt)

def split_item(item: Item) -> dict[str, Fraction]:
    """Calculate each person's exact fractional share of an item in cents
    
    Args:
        item (Item): Item containing price and people sharing item

    Returns:
        dict[str, Fraction]: Dictionary with a person's name as key and persons fractional share as value
    """
    if not item.shared_by:
        raise ValueError("No person attached to item")

    cents = int(item.price * item.quantity * 100)

    split = {}

    for person in item.shared_by:

        split[person.name] = Fraction(cents, len(item.shared_by))

    return split

def calculate_person_subtotal(receipt: Receipt) -> dict[str, int]:
    """Calculate and fairly round each person's share of receipt subtotal
    
    Args:
        receipt (Receipt): Receipt containing people splitting receipt and items

    Returns:
        dict[str, int]: Dictionary with a person's name as key and persons subtotal in cents as value
    """
    
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
    """Convert fractional cent allocations into whole cents while preserving total
    
    Args:
        allocations (dict[str, Fraction]): Dictonary with person's name as key and fractional split in cents for person
        total_cents (int): Total number of sents to be split and allocated

    Returns:
        dict[str, int]: Dictionary with person's name as key and whole cent allocations as value
    """
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
    """Calculate proportional amount of tax a person must pay
    
    Args:
        receipt (Receipt): Receipt containing subtotal and tax amount in dollars
        subtotals (dict[str, int]): Dictionary with person's name as key and subtotal for person in cents as value

    Returns:
        dict[str, int]: Dictionary with person's name as key and proportional amount of tax for person in cents
    """
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
    """Calculate proportional amount of tip a person must pay
    
    Args:
        receipt (Receipt): Receipt containing subtotal and tip amount in dollars
        subtotals (dict[str, int]): Dictionary with person's name as key and subtotal for person in cents as value

    Returns:
        dict[str, int]: Dictionary with person's name as key and proportional amount of tip for person in cents
    """
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
    """Calculates final total each person must pay in dollar value

    Args:
        subtotals (dict[str, int]): Dictionary with person's name as key and subtotal for person in cents as value
        tax_allocations (dict[str, int]): Dictionary with person's name as key and proportional amount of tax for person in cents
        tip_allocations (dict[str, int]): Dictionary with person's name as key and proportional amount of tip for person in cents
    
    Return:
        dict[str, Decimal]: Dictionary with person's name as key and final total to be paid per person in dollar value
    """
    totals = {}
    for name in subtotals:
        totals[name] = Decimal(subtotals[name] + tax_allocations[name] + tip_allocations[name]) / Decimal("100")

    return totals

def calculate_bill(receipt: Receipt) -> dict[str, Decimal]:
    """Calculates final amount owed for each person in dollars

    Args: 
        receipt (Receipt): Receipt containing items, people splitting receipt, subtotal, tax, tip, and total

    Returns:
        dict[str, Decimal]: Dictionary with person's name as key and final total to be paid per person in dollar value
    """

    if not validate_subtotal(receipt):
        raise ValueError("Receipt subtotal does not match summed item subtotal")

    subtotals = calculate_person_subtotal(receipt)
    tax_allocations = calculate_person_tax(receipt, subtotals)
    tip_allocations = calculate_person_tip(receipt, subtotals)
    final_split = calculate_final_totals(subtotals, tax_allocations, tip_allocations)

    if sum(final_split.values()) != receipt.total:
        raise ValueError("Split total does not match receipt total")

    return final_split