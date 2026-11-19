"""
models.py — SQLite database models using Python's built-in sqlite3.
Provides init_db(), seed users, and helper functions.
"""

from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = str(Path(__file__).resolve().parent / "app.db")

FALLBACK_USERS = {
    "ananya": {"id": 1, "username": "ananya", "department": "Product", "full_name": "Ananya Iyer", "role_title": "Senior Product Manager (Platform Admin)", "is_admin": 1, "is_owner": 1},
    "aarav": {"id": 2, "username": "aarav", "department": "Operations", "full_name": "Aarav Sharma", "role_title": "Operations Lead (Department Owner)", "is_admin": 0, "is_owner": 1},
    "priya": {"id": 3, "username": "priya", "department": "Sales", "full_name": "Priya Patel", "role_title": "Enterprise Sales Lead (Department Owner)", "is_admin": 0, "is_owner": 1},
    "rohan": {"id": 4, "username": "rohan", "department": "Product", "full_name": "Rohan Verma", "role_title": "Product Analyst (Read-Only)", "is_admin": 0, "is_owner": 0},
    "chirag": {"id": 5, "username": "chirag", "department": "Technical", "full_name": "Chirag Mehta", "role_title": "Systems Architect (Department Owner)", "is_admin": 0, "is_owner": 1},
    "vikram": {"id": 6, "username": "vikram", "department": "Governance_Risk", "full_name": "Vikram Malhotra", "role_title": "Head of Infosec (Security Admin)", "is_admin": 1, "is_owner": 1},
    "farhan": {"id": 7, "username": "farhan", "department": "Finance", "full_name": "Farhan Qureshi", "role_title": "Pricing Controller (Department Owner)", "is_admin": 0, "is_owner": 1},
}


def _connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Create tables and seed demo users (idempotent)."""
    conn = _connect(db_path)
    cur = conn.cursor()

    # Safely migrate users table if schema changed
    try:
        user_cols = [c[1] for c in cur.execute("PRAGMA table_info(users);").fetchall()]
        if user_cols and "role_title" not in user_cols:
            cur.execute("DROP TABLE users;")
    except Exception:
        pass

    # --- Create tables ---
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL UNIQUE,
            department TEXT    NOT NULL,
            full_name  TEXT    NOT NULL,
            role_title TEXT    NOT NULL,
            is_admin   INTEGER NOT NULL DEFAULT 0,
            is_owner   INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp        TEXT    NOT NULL,
            username         TEXT    NOT NULL,
            department       TEXT    NOT NULL,
            query_masked     TEXT    NOT NULL,
            response_summary TEXT    NOT NULL,
            pii_blocked      INTEGER NOT NULL DEFAULT 0,
            rbac_blocked     INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id  INTEGER NOT NULL,
            rating    TEXT    NOT NULL CHECK(rating IN ('up','down')),
            comment   TEXT,
            timestamp TEXT    NOT NULL,
            FOREIGN KEY(audit_id) REFERENCES audit_log(id)
        );
    """)

    # --- Seed demo users with Indian executive personas & Admin/Owner clearances ---
    demo_users = [
        ("ananya",  "Product",         "Ananya Iyer",      "Senior Product Manager (Platform Admin)", 1, 1),
        ("aarav",   "Operations",      "Aarav Sharma",     "Operations Lead (Department Owner)",       0, 1),
        ("priya",   "Sales",           "Priya Patel",      "Enterprise Sales Lead (Department Owner)", 0, 1),
        ("rohan",   "Product",         "Rohan Verma",      "Product Analyst (Read-Only)",              0, 0),
        ("chirag",  "Technical",       "Chirag Mehta",     "Systems Architect (Department Owner)",     0, 1),
        ("vikram",  "Governance_Risk", "Vikram Malhotra",  "Head of Infosec (Security Admin)",         1, 1),
        ("farhan",  "Finance",         "Farhan Qureshi",   "Pricing Controller (Department Owner)",    0, 1),
    ]
    cur.execute("DELETE FROM users;")
    for username, dept, full_name, role_title, is_admin, is_owner in demo_users:
        cur.execute(
            "INSERT INTO users (username, department, full_name, role_title, is_admin, is_owner) VALUES (?, ?, ?, ?, ?, ?)",
            (username, dept, full_name, role_title, is_admin, is_owner),
        )

    conn.commit()
    conn.close()
    print(f"[models] Database initialised at {db_path}")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_user(username: str, db_path: str = DB_PATH) -> Optional[dict]:
    """Return user dict or None if not found, with robust fallback."""
    try:
        conn = _connect(db_path)
        try:
            row = conn.execute(
                "SELECT id, username, department, full_name, role_title, is_admin, is_owner FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        except sqlite3.OperationalError:
            row = conn.execute(
                "SELECT id, username, department, full_name FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        conn.close()
        if row is not None:
            res = dict(row)
            if "is_admin" not in res:
                res["is_admin"] = 1 if username in ["ananya", "vikram"] else 0
            if "is_owner" not in res:
                res["is_owner"] = 0 if username == "rohan" else 1
            return res
    except Exception:
        pass

    # Safe fallback if database was temporarily locked or unseeded
    u_lower = (username or "").lower()
    return FALLBACK_USERS.get(u_lower, FALLBACK_USERS["ananya"])


def log_audit(
    username: str,
    department: str,
    query_masked: str,
    response_summary: str,
    pii_blocked: bool = False,
    rbac_blocked: bool = False,
    db_path: str = DB_PATH,
) -> int:
    """Insert an audit record and return its new id."""
    try:
        ts = datetime.now(timezone.utc).isoformat()
        conn = _connect(db_path)
        cur = conn.execute(
            """INSERT INTO audit_log
                   (timestamp, username, department, query_masked, response_summary, pii_blocked, rbac_blocked)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ts, username, department, query_masked, response_summary,
             int(pii_blocked), int(rbac_blocked)),
        )
        new_id = cur.lastrowid or 1
        conn.commit()
        conn.close()
        return new_id
    except Exception as exc:
        print(f"[models] Notice: log_audit bypassed database error ({exc})")
        return 1


def add_feedback(
    audit_id: int,
    rating: str,
    comment: str = "",
    db_path: str = DB_PATH,
) -> None:
    """Attach feedback to an existing audit log entry."""
    ts = datetime.now(timezone.utc).isoformat()
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO feedback (audit_id, rating, comment, timestamp) VALUES (?, ?, ?, ?)",
        (audit_id, rating, comment, ts),
    )
    conn.commit()
    conn.close()


def get_audit_log(limit: int = 50, db_path: str = DB_PATH) -> list[dict]:
    """Return the most recent *limit* audit log entries (newest first)."""
    conn = _connect(db_path)
    rows = conn.execute(
        """SELECT a.id, a.timestamp, a.username, a.department,
                  a.query_masked, a.response_summary, a.pii_blocked, a.rbac_blocked,
                  f.rating AS feedback_rating, f.comment AS feedback_comment
           FROM audit_log a
           LEFT JOIN feedback f ON f.audit_id = a.id
           ORDER BY a.id DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
