"""
routers/audit_router.py — Audit log and feedback endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import get_audit_log, add_feedback

router = APIRouter(prefix="/audit", tags=["audit"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class FeedbackPayload(BaseModel):
    rating: str           # "up" or "down"
    comment: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/logs")
async def get_logs(limit: int = 50):
    """
    Return the most recent *limit* audit log entries (newest first).
    Each entry includes a joined feedback row (if any).
    """
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    entries = get_audit_log(limit=limit)
    return {"count": len(entries), "logs": entries}


@router.post("/feedback/{audit_id}")
async def post_feedback(audit_id: int, payload: FeedbackPayload):
    """
    Submit thumbs-up / thumbs-down feedback for a specific audit log entry.
    """
    if payload.rating not in ("up", "down"):
        raise HTTPException(
            status_code=422,
            detail="rating must be 'up' or 'down'",
        )
    try:
        add_feedback(audit_id=audit_id, rating=payload.rating, comment=payload.comment)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "ok", "audit_id": audit_id, "rating": payload.rating}
