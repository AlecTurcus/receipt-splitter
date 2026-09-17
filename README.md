# Receipt Splitter

A web app that extracts items from a receipt and calculates how much each person owes when splitting a bill

[Live Demo](https://receipt-splitter-vert.vercel.app/)

## Features

- Extract receipt items, quantities, and pricing information using AI
- Allow users to review and edit extracted receipt data
- Add and remove people to a receipt
- Add and remove receipt items
- Assign people to individual or shared items
- Split tax and tip proportionally
- Calculate final totals for each person

## How It Works
1. User uploads a receipt image.
2. Gemini extracts receipt items, quantities, and pricing information.
3. User reviews and corrects extracted data if needed.
4. User assigns people to individual or shared items.
5. Calculation engine splits item costs, tax, and tip.

## Tech Stack

- React
- TypeScript
- FastAPI
- Python
- Pydantic
- Gemini API
- pytest
- Vite
- Render
- Vercel

## Running Locally

Backend:

```bash
python -m pip install -e .
python -m uvicorn receipt_splitter.api:app --reload
```

Create a `.env` file inside the project root:

```env
GEMINI_API_KEY=your_api_key
FRONTEND_URL=http://localhost:5173
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file inside the `frontend` directory:

```env
VITE_API_URL=http://127.0.0.1:8000
```