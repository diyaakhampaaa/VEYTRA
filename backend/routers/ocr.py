from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class OCRResult(BaseModel):
    plate: str
    confidence: float
    alternatives: List[str]


router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/")
def receive_ocr(data: OCRResult):
    return {
        "message": "OCR data received",
        "data": data
    }