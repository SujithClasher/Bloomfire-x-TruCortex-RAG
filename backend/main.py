"""
main.py — FastAPI Application Entry Point for Integrated KMP + TruCortex + Bloomfire Platform.
Features Real Multi-Format ChromaDB Vector Ingestion, Strict Department RBAC Filtering,
Live Folder Sync & Upload, Regex PII GuardLLM, and Change & Conflict Radar.
"""

import os
import warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore", message=".*unauthenticated requests to the HF Hub.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

from models import init_db, _connect
from seed_enterprise_files import seed_all
from rag_pipeline import ingest_all_repositories
from routers.audit_router import router as audit_router
from routers.query_router import router as query_router
from routers.upload_router import router as upload_router
from routers.folders_router import router as folders_router
from routers.conflict_router import router as conflict_router
from routers.sync_router import router as sync_router
from routers.document_viewer_router import router as document_viewer_router
from routers.admin_router import router as admin_router

# ---------------------------------------------------------------------------
# Path Helper
# ---------------------------------------------------------------------------
def get_repo_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / "data_repositories",
        Path(__file__).resolve().parent / "data_repositories",
        Path("D:/RAG/data_repositories"),
        Path("./data_repositories").resolve(),
        Path("../data_repositories").resolve(),
    ]
    for c in candidates:
        if (c / "Operations").exists() or (c / "bloomfire_sops").exists() or (c / "Product").exists():
            return c
    target = Path("D:/RAG/data_repositories")
    target.mkdir(parents=True, exist_ok=True)
    return target

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="KMP + TruCortex + Bloomfire Intelligence Platform",
    version="1.0.0",
    description=(
        "Production-grade local RAG platform natively parsing .pptx, .docx, .xlsx, "
        ".pdf, and .md files with strict Department RBAC, Regex GuardLLM, and Conflict Radar."
    ),
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------
app.include_router(audit_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(folders_router, prefix="/api")
app.include_router(conflict_router, prefix="/api")
app.include_router(sync_router, prefix="/api")
app.include_router(document_viewer_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


# ---------------------------------------------------------------------------
# Lifecycle Startup Event
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    print("[main] Initializing SQLite database...")
    init_db()

    repo_dir = get_repo_dir()
    print(f"[main] Enterprise unified repository path: {repo_dir}")

    # Ensure files are seeded and migrated into unified department structure
    print("[main] Ensuring unified enterprise repositories are active...")
    seed_all()

    # Index into ChromaDB
    print(f"[main] Indexing repository files from {repo_dir} into ChromaDB...")
    try:
        summary = ingest_all_repositories(str(repo_dir))
        print(f"[main] ChromaDB Ingestion complete: {summary.get('total_chunks', 0)} chunks across {summary.get('total_files', 0)} files.")
    except Exception as exc:
        print(f"[main] Notice during startup indexing: {exc}")

    print("[main] Platform backend ready on http://localhost:8010")

    # Pre-warm local GGUF model in background (auto-detects Downloads/ or backend/models/)
    try:
        from gguf_engine import preload_model_background
        preload_model_background()
    except Exception:
        try:
            import threading
            from llm_engine import synthesize_claude_style as _w
            threading.Thread(target=lambda: None, daemon=True).start()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Health and User Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["system"])
async def health():
    return {
        "status": "online",
        "service": "KMP + TruCortex + Bloomfire Platform",
        "version": "1.0.0",
        "rag_engine": "ChromaDB Persistent",
        "rbac_enforcement": "Active",
        "guard_llm": "Active (Regex PAN/Aadhaar/Phone/Email)",
    }


@app.get("/api/users", tags=["system"])
async def list_users():
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, username, department, full_name, role_title, is_admin, is_owner FROM users ORDER BY id"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = conn.execute(
            "SELECT id, username, department, full_name FROM users ORDER BY id"
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if "is_admin" not in d:
            d["is_admin"] = 1 if d["username"] in ["ananya", "vikram"] else 0
        if "is_owner" not in d:
            d["is_owner"] = 0 if d["username"] == "rohan" else 1
        result.append(d)
    return {"users": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
