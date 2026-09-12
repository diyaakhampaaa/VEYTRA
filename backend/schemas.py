from pydantic import BaseModel
from typing import List, Optional


class Detection(BaseModel):
    camera_id: str
    timestamp: str
    source: str
    detections: List[dict]