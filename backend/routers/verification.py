from fastapi import APIRouter, HTTPException
from typing import Any

from ai.verification.integration import process_verification_payloads

router = APIRouter(
    prefix="/verification",
    tags=["Verification"],
)


@router.post("/run")
def run_verification(payloads: list[dict[str, Any]]):
    """
    Run Member 4 verification pipeline on Member 3 payloads.
    """

    try:
        results = process_verification_payloads(payloads)

        return {
            "status": "success",
            "count": len(results),
            "results": results,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Verification pipeline failed: {str(error)}",
        )