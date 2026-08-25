from pydantic import BaseModel, Field
from decimal import Decimal

class Item(BaseModel) :
    name: str
    price: Decimal
    shared_by: list[str] = Field(default_factory = list)

class Receipt(BaseModel):
    items: list[Item]
    subtotal: Decimal
    tax: Decimal
    tip: Decimal
    total: Decimal
