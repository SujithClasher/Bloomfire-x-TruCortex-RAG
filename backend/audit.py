"""
audit.py — Thin wrapper around models.log_audit that also logs to console.
"""

from datetime import datetime, timezone
from models import log_audit as _log_audit, add_feedback as _add_feedback


def log_audit(
    username: str,
    department: str,
    query_masked: str,
    response_summary: str,
    pii_blocked: bool = False,
    rbac_blocked: bool = False,
) -> int:
    """
    Persist an audit record and echo a one-line summary to stdout.
    Returns the new audit log ID.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    flags = []
    if pii_blocked:
        flags.append("PII_BLOCKED")
    if rbac_blocked:
        flags.append("RBAC_BLOCKED")
    flag_str = f" [{', '.join(flags)}]" if flags else ""

    print(
        f"[AUDIT] {ts} | user={username} dept={department}{flag_str} | "
        f"query={query_masked[:80]!r}"
    )

    return _log_audit(
        username=username,
        department=department,
        query_masked=query_masked,
        response_summary=response_summary,
        pii_blocked=pii_blocked,
        rbac_blocked=rbac_blocked,
    )


def add_feedback(audit_id: int, rating: str, comment: str = "") -> None:
    """Record thumbs-up / thumbs-down feedback for an audit log entry."""
    print(f"[FEEDBACK] audit_id={audit_id} rating={rating!r} comment={comment!r}")
    _add_feedback(audit_id=audit_id, rating=rating, comment=comment)
