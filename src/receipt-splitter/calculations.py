from models import Receipt, Item, Person
from decimal import Decimal

def calculate_subtotal(receipt: Receipt):
    calculated_subtotal = sum(item.price for item in receipt.items)
    return calculated_subtotal

def validate_subtotal(receipt: Receipt):
    return receipt.subtotal == calculate_subtotal(receipt)

def split_item(item: Item):
    if not item.shared_by:
        raise ValueError("No person attached to item")

    cents = int(item.price * 100)

    base_share = cents // len(item.shared_by)

    remainder = cents % len(item.shared_by)

    split = {}

    for person in item.shared_by:

        if remainder:
            share = Decimal(base_share + 1) / Decimal(100)
            remainder -= 1
        else:
            share = Decimal(base_share) / Decimal(100)

        split[person.name] = share

    return split