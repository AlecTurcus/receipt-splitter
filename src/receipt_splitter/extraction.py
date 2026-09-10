from dotenv import load_dotenv
from google import genai
from .models import ExtractedReceipt, Receipt, Item
from decimal import Decimal, InvalidOperation
import base64

load_dotenv()
client = genai.Client()

def extract_receipt(image_bytes: bytes, mime_type: str) -> ExtractedReceipt:
    """Uses AI to extract pertinent info from receipt and output it in usable format
    
    Args:
        image_bytes (bytes): Raw bytes of image data
        mime_type (str): MIME type of file
    
    Returns:
        ExtractedReceipt: Structured receipt info extracted from image
    """

    image_data = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """Extract the receipt information from the image.

    Rules:
    - Extract each purchased item.
    - For each item, extract the quantity explicitly shown on the receipt.
    - If no quantity is explicitly shown, or the quantity cannot be read, use 1.
    - Do not treat numbers that are part of an item name or description as the quantity.
    - For each item, extract the explicitly shown per-unit price as unit_price.
    - For each item, extract the total amount charged for the entire item line as line_total.
    - line_total must represent the total for the whole line, not the per-unit price.
    - If unit_price or line_total is not explicitly shown, reutrn "0.00" for that field.
    - Do not calculate unit_price from line_total or line_total from unit_price.
    - Do not combine separate repeated item lines into one item.
    - Extract the subtotal, tax, tip, and total.
    - For all monetary values, return only the numeric decimal value.
    - If a monetary value cannot be read or is not present, return "0.00" for the value.
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
    """Converts string value to decimal value

    Args:
        value (str): String value to convert

    Returns:
        Decimal: String value converted to Decimal, or 0.00 if conversion fails
    """
    try:
        return Decimal(value)
    except InvalidOperation:
        return Decimal("0.00")

def extracted_to_receipt(extracted: ExtractedReceipt) -> Receipt:
    """Convert an ExtractedReceipt into a Receipt

    Args:
        extracted (ExtractedReceipt): Receipt info extracted by AI

    Returns:
        Receipt: Receipt containing Decimal values and items
    """
    items = []

    for item in extracted.items:
        line_total = parse_money(item.line_total)
        unit_price = parse_money(item.unit_price)
    
        if line_total != Decimal("0.00"):
            price = line_total / item.quantity
        else:
            price = unit_price

        items.append(
            Item(
                name = item.name,
                price = price,
                quantity = item.quantity
            )
        )
    return Receipt(
        items = items,
        subtotal = parse_money(extracted.subtotal),
        tax = parse_money(extracted.tax),
        tip = parse_money(extracted.tip),
        total = parse_money(extracted.total)
    )