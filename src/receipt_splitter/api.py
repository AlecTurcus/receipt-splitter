import os

from .extraction import extract_receipt, extracted_to_receipt
from .models import Receipt
from .calculations import calculate_bill

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024

load_dotenv()
frontend_url = os.getenv("FRONTEND_URL")

if not frontend_url:
    raise RuntimeError("FRONTEND_URL environment variable not set")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/receipts/extract")
async def extract_receipt_endpoint(file: UploadFile = File(...)):
    """Extract receipt information from uploaded image
    
    Args:
        file (UploadFile): Receipt image uploaded by user

    Returns:
        Receipt: Receipt containing extracted items and monetary values
    """

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415, 
            detail="Unsupported file type"
        )
    
    image_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large"
        )

    try:
        extracted = extract_receipt(image_bytes, file.content_type)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Receipt extraction service temporarily unavailable"
        )
    return extracted_to_receipt(extracted)


@app.post("/receipts/calculate")
def calculate_receipt(receipt: Receipt):
    """Calculates dollar amount owed by each person for a receipt

    Args:
        receipt (Receipt): Completed receipt containing item assignments and totals

    Returns:
        dict[str, Decimal]: Final dollar amount owed by each person
    """

    try:
        return calculate_bill(receipt)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.get("/wake")
def wake():
    """Wake backend server when web app loads"""
    return {"server": "I'm awake"}

