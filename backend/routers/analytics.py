from fastapi import APIRouter, HTTPException
from typing import Any
import pandas as pd

from analytics.congestion import compute_congestion

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.post("/congestion")
def congestion(data: list[dict[str, Any]]):
    try:
        events = pd.DataFrame(data)

        result = compute_congestion(
            events,
            as_json=True
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Congestion analysis failed: {str(error)}"
        )