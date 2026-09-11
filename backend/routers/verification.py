from fastapi import APIRouter, HTTPException
from typing import Any

from ai.verification.integration import process_verification_payloads

router = APIRouter(
    prefix="/verification",
    tags=["Verification"],
)


# Temporary in-memory store for verification results.
# Later this can be replaced with PostgreSQL.
verification_events: list[dict[str, Any]] = []


@router.post("/run")
def run_verification(payloads: list[dict[str, Any]]):
    """
    Run Member 4 verification pipeline on Member 3 payloads.
    """

    try:
        results = process_verification_payloads(payloads)

        # Store the latest verification results
        verification_events.clear()
        verification_events.extend(results)

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


@router.get("/events")
def get_verification_events():
    """
    Return verification events for the VEYTRA dashboard.
    """

    return {
        "status": "success",
        "count": len(verification_events),
        "events": verification_events,
    }