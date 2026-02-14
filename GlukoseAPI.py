from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from pathlib import Path
import csv
import time
import asyncio
import os
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

API_PASSWORD = os.getenv("API_PASSWORD", "change-me")
app = FastAPI()

CSV_DIR = Path("data").resolve()

# jednoduchý in-memory rate limit (1 req / 1s)
last_request_time = 0.0
lock = asyncio.Lock()


EXCLUDED_PATHS = {
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
}
def verify_api_password(x_api_password: str = Header(...)):
    if x_api_password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid API password")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://130.162.239.159:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

RATE_LIMIT = 5
WINDOW_SECONDS = 1.0

request_times = []
lock = asyncio.Lock()
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    async with lock:
        now = time.time()

        # odstranit staré requesty mimo časové okno
        while request_times and request_times[0] <= now - WINDOW_SECONDS:
            request_times.pop(0)

        if len(request_times) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
            )

        request_times.append(now)

    return await call_next(request)


def read_csv_sync(path: Path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows.extend(reader)
    return rows


@app.post("/download/", dependencies=[Depends(verify_api_password)])
async def download(date: str, name: str):
    filename = f"{date}_{name}_glucose.csv"
    file_path = (CSV_DIR / filename).resolve()

    # bezpečná kontrola proti path traversal
    if not file_path.is_file() or CSV_DIR not in file_path.parents:
        raise HTTPException(status_code=404, detail="CSV file not found")

    rows = await asyncio.to_thread(read_csv_sync, file_path)
    return rows

@app.get("/download-csv/", dependencies=[Depends(verify_api_password)])
async def download_csv(date: str, name: str):
    filename = f"{date}_{name}_glucose.csv"
    file_path = (CSV_DIR / filename).resolve()

    if not file_path.is_file() or CSV_DIR not in file_path.parents:
        raise HTTPException(status_code=404, detail="CSV file not found")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=filename,
    )
def extract_date_from_filename(filename: str) -> datetime:
    date_str = filename.split("_")[0]
    return datetime.strptime(date_str, "%Y-%m-%d")

DATA_DIR = "data"
@app.get("/all_data", dependencies=[Depends(verify_api_password)])
async def all_data(name: str):
    records = []

    files = [
        f for f in os.listdir(DATA_DIR)
        if f.endswith(".csv")
    ]

    # seřazení podle data v názvu souboru
    files.sort(key=extract_date_from_filename)

    for filename in files:
        path = os.path.join(DATA_DIR, filename)

        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                records.append({
                    "timestamp": row["timestamp"],
                    "glucose": float(row["glucose"]),
                    "unit": row["unit"]
                })

    return records