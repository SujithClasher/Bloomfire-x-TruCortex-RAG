"""
routers/admin_router.py — Enterprise Admin Console Endpoints.
Manages Department Ownership Matrix, User Role Elevations,
GuardLLM Security Policies, and System Telemetry.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path

from models import get_user, init_db, DB_PATH
from guard_llm import scan_input, mask_output
from rag_pipeline import get_collection

router = APIRouter(prefix="/admin", tags=["admin"])


class RoleUpdatePayload(BaseModel):
    username: str
    is_admin: Optional[bool] = None
    is_owner: Optional[bool] = None
    role_title: Optional[str] = None


class GuardLLMTestPayload(BaseModel):
    text: str


def _get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/overview")
async def get_admin_overview():
    """Return consolidated platform administration statistics and ownership directory."""
    conn = _get_db()
    try:
        users = [dict(r) for r in conn.execute(
            "SELECT id, username, department, full_name, role_title, is_admin, is_owner FROM users ORDER BY id"
        ).fetchall()]
    except Exception:
        users = []
    
    audit_count = conn.execute("SELECT COUNT(*) AS total FROM audit_log").fetchone()["total"]
    pii_blocked_count = conn.execute("SELECT COUNT(*) AS total FROM audit_log WHERE pii_blocked = 1").fetchone()["total"]
    rbac_blocked_count = conn.execute("SELECT COUNT(*) AS total FROM audit_log WHERE rbac_blocked = 1").fetchone()["total"]
    conn.close()

    admins = [u for u in users if u.get("is_admin")]
    owners = [u for u in users if u.get("is_owner") and not u.get("is_admin")]
    analysts = [u for u in users if not u.get("is_owner") and not u.get("is_admin")]

    return {
        "status": "healthy",
        "system": {
            "name": "KMP + TruCortex + Bloomfire Platform",
            "version": "1.0.0",
            "port": 8010,
            "architecture": "Local Extractive Grounded RAG (Zero External LLMs, Zero API Keys)",
            "vector_store": "ChromaDB Persistent (hnsw:space: cosine)",
            "database": "SQLite 3 (WAL mode)",
        },
        "metrics": {
            "total_users": len(users),
            "platform_admins": len(admins),
            "department_owners": len(owners),
            "analysts": len(analysts),
            "total_audit_events": audit_count,
            "pii_intercepts": pii_blocked_count,
            "rbac_interceptions": rbac_blocked_count,
        },
        "users": users,
        "guard_rules": [
            {
                "rule_name": "PAN National Identity Filter",
                "pattern": r"[A-Z]{5}[0-9]{4}[A-Z]",
                "action": "STRICT_BLOCK_HTTP_422",
                "severity": "CRITICAL",
                "description": "Indian Permanent Account Number regex inspection; stops vector search instantly.",
            },
            {
                "rule_name": "12-Digit National Identity Filter",
                "pattern": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
                "action": "STRICT_BLOCK_HTTP_422",
                "severity": "CRITICAL",
                "description": "National biometric / Aadhaar sequence verification.",
            },
            {
                "rule_name": "Mobile Number Token Sanitizer",
                "pattern": r"\b(?:\+91|0)?[6-9]\d{9}\b",
                "action": "MASK_TRANSFORM",
                "severity": "MEDIUM",
                "description": "Anonymizes customer phone numbers to [PHONE_MASKED].",
            },
            {
                "rule_name": "Email Address Token Sanitizer",
                "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                "action": "MASK_TRANSFORM",
                "severity": "MEDIUM",
                "description": "Anonymizes corporate email addresses to [EMAIL_MASKED].",
            },
        ],
    }


@router.post("/users/update-role")
async def update_user_role(payload: RoleUpdatePayload):
    """Admin action to promote/demote department ownership or platform admin rights."""
    conn = _get_db()
    existing = conn.execute("SELECT * FROM users WHERE username = ?", (payload.username,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"User '{payload.username}' not found.")

    new_is_admin = int(payload.is_admin) if payload.is_admin is not None else existing["is_admin"]
    new_is_owner = int(payload.is_owner) if payload.is_owner is not None else existing["is_owner"]
    new_title = payload.role_title if payload.role_title is not None else existing["role_title"]

    conn.execute(
        "UPDATE users SET is_admin = ?, is_owner = ?, role_title = ? WHERE username = ?",
        (new_is_admin, new_is_owner, new_title, payload.username),
    )
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "username": payload.username,
        "is_admin": bool(new_is_admin),
        "is_owner": bool(new_is_owner),
        "role_title": new_title,
        "message": f"Updated clearance for {payload.username} successfully.",
    }


@router.post("/test-guardllm")
async def test_guard_llm(payload: GuardLLMTestPayload):
    """Live interactive testing playground for Regex GuardLLM security checks."""
    result = scan_input(payload.text)
    masked = mask_output(payload.text)
    return {
        "input_text": payload.text,
        "blocked": result["blocked"],
        "reason": result["reason"],
        "masked_preview": masked,
        "status": "BLOCKED (HTTP 422)" if result["blocked"] else "PASSED_SANITIZED",
    }
