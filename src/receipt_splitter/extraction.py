from dotenv import load_dotenv
from google import genai
from .models import ExtractedReceipt, Receipt, Item
from decimal import Decimal, InvalidOperation
import base64

load_dotenv()
client = genai.Client()

def extract_receipt(image_bytes: bytes, mime_type: str) -> ExtractedReceipt:

    image_data = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """Extract the receipt information from the image.

    Rules:
    - Extract each purchased item and its line price.
    - Extract the subtotal, tax, tip, and total.
    - For all monetary values, return only the numeric decimal value.
    - If a monetary value cannot be read or is not present, return "0.00" for that value
    - Do not calculate or infer missing monetary values.
    - Do not include subtotal, tax, tip, or total as purchased items.
    """

    response = client.interactions.create(
        model = "gemini-3.5-flash-lite",
        input = [
            {
                "type": "image",
                "data": image_data,
                "mime_type": mime_type
            },
            {
                "type": "text",
                "text": prompt
            }
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ExtractedReceipt.model_json_schema()
        }
    )

    return ExtractedReceipt.model_validate_json(response.output_text)

def parse_money(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation:
        return Decimal("0.00")

def extracted_to_receipt(extracted: ExtractedReceipt) -> Receipt:
    items = []

    for item in extracted.items:
        items.append(
            Item(
                name = item.name,
                price = parse_money(item.price)
            )
        )
    return Receipt(
        items = items,
        subtotal = parse_money(extracted.subtotal),
        tax = parse_money(extracted.tax),
        tip = parse_money(extracted.tip),
        total = parse_money(extracted.total)
    )