from fastapi import FastAPI, UploadFile, File, HTTPException
from .extraction import extract_receipt, extracted_to_receipt
from .models import Receipt
from .calculations import calculate_bill


app = FastAPI()

@app.post("/receipts/extract")
async def extract_receipt_endpoint(file: UploadFile = File(...)):
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(415, "Unsupported file type")
    
    image_bytes = await file.read()

    try:
        extracted = extract_receipt(image_bytes, file.content_type)
    except Exception:
        raise HTTPException(503, "Receipt extraction service temporarily unavailable")
    return extracted_to_receipt(extracted)

@app.post("/receipts/calculate")
def calculate_receipt(receipt: Receipt):

    try:
        return calculate_bill(receipt)
    except ValueError as error:
        raise HTTPException(400, str(error))

