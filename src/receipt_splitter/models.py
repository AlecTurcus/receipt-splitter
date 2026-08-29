from pydantic import BaseModel, Field
from decimal import Decimal

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

class Person(BaseModel):
    name: str
