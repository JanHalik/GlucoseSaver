from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from pathlib import Path
import csv
import time
import asyncio
import os

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

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    global last_request_time

    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    async with lock:
        now = time.time()
        if now - last_request_time < 1.0:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
            )
        last_request_time = now

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