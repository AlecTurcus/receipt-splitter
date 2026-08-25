from models import Receipt, Item

def calculate_subtotal(receipt: Receipt):
    calculated_subtotal = sum(item.price for item in receipt.items)
    return calculated_subtotal

def validate_subtotal(receipt: Receipt):
    return receipt.subtotal == calculate_subtotal(receipt)
