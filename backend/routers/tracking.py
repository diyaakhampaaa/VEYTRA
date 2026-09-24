from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from sqlalchemy.orm import Session

from ai.tracking.integration import (
    match_tracked_frames,
    prepare_track_records,
)
from backend.database import SessionLocal
from backend.services.trajectory_persistence import persist_trajectories


router = APIRouter(prefix="/tracking", tags=["Tracking"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/match")
def match_tracks(
    tracked_frames: list[dict[str, Any]],
    db: Session = Depends(get_db),
):
    """
    Match completed local tracks across cameras,
    reconstruct trajectories, and persist them to the database.

    Input:
        A list of Member 3 enriched frame results.

    Output:
        Global vehicle identities, trajectories,
        match scores, and verification candidates.
    """
    try:
        result = match_tracked_frames(tracked_frames)

        persisted_events = persist_trajectories(
            db,
            result.get("trajectories", []),
        )

        result["persisted_event_count"] = persisted_events

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