"""
routers/sync_router.py — Live Folder Sync & Full ChromaDB Ingestion Pipeline.
"""

import time
from pathlib import Path
from fastapi import APIRouter
from rag_pipeline import ingest_all_repositories
from seed_enterprise_files import seed_all

router = APIRouter(prefix="/sync", tags=["sync"])

def get_repo_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "data_repositories",
        Path(__file__).resolve().parent.parent / "data_repositories",
        Path("D:/RAG/data_repositories"),
        Path("./data_repositories").resolve(),
        Path("../data_repositories").resolve(),
    ]
    for c in candidates:
        if (c / "Operations").exists() or (c / "bloomfire_sops").exists() or (c / "Product").exists():
            return c
    return Path("D:/RAG/data_repositories")


@router.post("/reindex")
async def sync_and_reindex():
    """
    Run full live sync:
    1. Ensure all seed enterprise files exist on disk
    2. Ingest/re-index all multi-format files into persistent ChromaDB
    3. Return execution summary and statistics
    """
    t0 = time.perf_counter()
    
    try:
        seed_all()
    except Exception as exc:
        print(f"[sync] Notice during seed check: {exc}")
    
    try:
        repo_dir = get_repo_dir()
        summary = ingest_all_repositories(str(repo_dir))
        t1 = time.perf_counter()
        summary["duration_seconds"] = round(t1 - t0, 2)
        summary["status"] = "success"
        return summary
    except Exception as exc:
        print(f"[sync] Error during ingestion: {exc}")
        return {
            "total_files": 0,
            "total_chunks": 0,
            "status": "error",
            "error": str(exc),
            "duration_seconds": round(time.perf_counter() - t0, 2)
        }
