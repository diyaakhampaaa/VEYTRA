"""Standalone FastAPI app for the READ stage: POST /ocr."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

# Allow `uvicorn ai.ocr.api:app` from the repo root.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ai.ocr.ocr_engine import read_plate

app = FastAPI(
    title="VEYTRA OCR",
    description="Member 2 READ stage — plate crop in, normalized plate JSON out.",
    version="1.0.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "VEYTRA OCR", "stage": "READ"}


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(..., description="Plate crop image")) -> dict:
    try:
        payload = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read upload: {exc}") from exc
    return read_plate(payload)
