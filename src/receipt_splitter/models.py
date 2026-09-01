from pydantic import BaseModel, Field
from decimal import Decimal


class Person(BaseModel):
    name: str

class Item(BaseModel) :
    name: str
    price: Decimal
    shared_by: list[Person] = Field(default_factory = list)

class Receipt(BaseModel):
    items: list[Item] = Field(default_factory = list)
    subtotal: Decimal
    tax: Decimal
    tip: Decimal
    total: Decimal
    people: list[Person] = Field(default_factory = list)

# Models for AI receipt extraction layer

class ExtractedItem(BaseModel):
    name: str
    price: str

class ExtractedReceipt(BaseModel):
    items: list[ExtractedItem]
    subtotal: str
    tax: str
    tip: str
    total: str