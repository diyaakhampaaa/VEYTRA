from fastapi import APIRouter
from backend.schemas import Detection

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/")
def receive_detection(data: Detection):
    return {
        "message": "Detection data received",
        "data": data
    }