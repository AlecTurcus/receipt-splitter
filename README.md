# Receipt Splitter

A web app that extracts items from a receipt and calculates how much each person owes when splitting a bill

## Features

- Extract receipt items using AI
- Allow users to review and edit extracted receipt data
- Add people to a receipt
- Assign peeople to individual or shared items
- Split tax and tip proportionally
- Calculate final totals for each person

## Tech Stack

- React
- TypeScript
- FastAPI
- Python
- Pydantic
- Gemini API

## Running Locally

Backend:

```bash
python -m uvicorn receipt_splitter.api:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```