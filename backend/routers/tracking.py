from fastapi import APIRouter, HTTPException
from typing import Any

from ai.tracking.integration import (
    match_tracked_frames,
    prepare_track_records,
)

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/match")
def match_tracks(tracked_frames: list[dict[str, Any]]):
    """
    Match completed local tracks across cameras.

    Input:
        A list of Member 3 enriched frame results.

    Output:
        Global vehicle identities, match scores,
        and verification candidates.
    """
    try:
        result = match_tracked_frames(tracked_frames)

        return {
            "status": "success",
            "data": result,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Cross-camera tracking failed: {str(error)}",
        )


@router.post("/prepare")
def prepare_tracks(tracked_frames: list[dict[str, Any]]):
    """
    Convert per-frame tracking results into completed
    camera-local track records.
    """
    try:
        records = prepare_track_records(tracked_frames)

        return {
            "status": "success",
            "track_records": records,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Track preparation failed: {str(error)}",
        )