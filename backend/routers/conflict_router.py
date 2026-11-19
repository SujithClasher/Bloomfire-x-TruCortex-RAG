"""
routers/conflict_router.py — Change & Conflict Radar API.
Manages detected semantic clashes (>0.65 similarity) across departmental boundaries,
with actions for "Confirm Impact" and "Dismiss".
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path

from conflict_radar import check_conflicts
from rag_pipeline import ingest_file

router = APIRouter(prefix="/conflicts", tags=["conflicts"])

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

# In-memory store of active conflict radar items with realistic cross-department contradictions
_CONFLICT_STORE: List[dict] = [
    {
        "id": 1,
        "source_file": "CV_CMR_Enterprise_Pitch_v2.1_APPROVED.pptx",
        "source_dept": "Sales",
        "source_location": "Slide 3: Enterprise Commercial Terms",
        "source_chunk": "Enterprise Tier Pricing: 35% volume discount applied for clients with >500k monthly queries (net rate: ₹18/pull). Quotes can be issued directly by Sales Leads.",
        "conflicting_file": "Bureau_Pricing_and_Rate_Card_v4.xlsx",
        "conflicting_dept": "Finance",
        "conflicting_location": "Sheet: Commercial_Tiers, Row 14",
        "conflicting_chunk": "Mandatory Pricing Floor: Maximum permissible discount across all tiers is 25% (absolute minimum floor rate: ₹24/pull). Any lower rate requires formal CFO approval.",
        "discrepancy_summary": "Sales pitch offers ₹18/pull (35% discount), but Finance Rate Card enforces a hard floor of ₹24/pull (25% max discount).",
        "similarity": 0.84,
        "conflict_type": "pricing_mismatch",
        "status": "active",
    },
    {
        "id": 2,
        "source_file": "Customer_Dispute_Resolution_SOP.docx",
        "source_dept": "Operations",
        "source_location": "Section 1.2: Triaging & Dispatch",
        "source_chunk": "All customer dispute correction requests must be dispatched synchronously to credit bureaus via real-time API endpoints within 4 business hours of receipt.",
        "conflicting_file": "API_Gateway_Endpoints.xlsx",
        "conflicting_dept": "Technical",
        "conflicting_location": "Sheet: Endpoints, Row 8",
        "conflicting_chunk": "Endpoint /v1/disputes/rectify is asynchronous batch-only (processing window: once daily at 02:00 UTC). Real-time synchronous dispatch is unsupported.",
        "discrepancy_summary": "Operations SOP mandates real-time API dispatch within 4 hours, but Technical Gateway only runs batch jobs once every 24 hours.",
        "similarity": 0.79,
        "conflict_type": "sla_architecture_clash",
        "status": "active",
    },
    {
        "id": 3,
        "source_file": "CV_CMR_Enterprise_Pitch_v2.1_APPROVED.pptx",
        "source_dept": "Sales",
        "source_location": "Slide 3: Model Transparency",
        "source_chunk": "Slide 3: CreditVision CMR provides enterprise clients with full audit transparency into internal model coefficients, neural network feature weights, and covariate rankings.",
        "conflicting_file": "Internal_Score_Methodology_CONFIDENTIAL.docx",
        "conflicting_dept": "Product",
        "conflicting_location": "Section 1: Formula Architecture",
        "conflicting_chunk": "STRICTLY CONFIDENTIAL: Raw model coefficients, GBDT feature weights, and TSM-2026 algorithms must never be shared externally under any circumstances or NDA.",
        "discrepancy_summary": "Sales pitch offers client audit access to proprietary model coefficients, which Product strictly classifies as trade-secret confidential.",
        "similarity": 0.88,
        "conflict_type": "confidentiality_breach",
        "status": "active",
    },
]
_CONFLICT_COUNTER = 4


def add_conflict_records(conflicts_list: list, source_file: str, source_dept: str) -> List[dict]:
    """Helper called by upload router to immediately register live radar clashes."""
    global _CONFLICT_STORE, _CONFLICT_COUNTER
    added = []
    for r in conflicts_list:
        c_item = {
            "id": _CONFLICT_COUNTER,
            "source_file": source_file,
            "source_dept": source_dept,
            "source_location": r.get("source_location", "Uploaded Section"),
            "source_chunk": r.get("source_chunk", ""),
            "conflicting_file": r.get("conflicting_file", ""),
            "conflicting_dept": r.get("conflicting_dept", ""),
            "conflicting_location": r.get("conflicting_location", "Vault Reference"),
            "conflicting_chunk": r.get("conflicting_chunk", ""),
            "discrepancy_summary": r.get("discrepancy_summary", f"Semantic divergence detected between {source_dept} and {r.get('conflicting_dept', '')} documentation."),
            "similarity": r.get("similarity", 0.0),
            "conflict_type": r.get("conflict_type", "policy_conflict"),
            "status": "active",
        }
        _CONFLICT_COUNTER += 1
        _CONFLICT_STORE.insert(0, c_item)
        added.append(c_item)
    return added


class ConflictActionPayload(BaseModel):
    action: str  # "confirm_impact" | "dismiss"
    notes: Optional[str] = ""


@router.get("/list")
async def list_conflicts(status_filter: Optional[str] = "active"):
    """List all detected conflicts in the radar."""
    if status_filter:
        filtered = [c for c in _CONFLICT_STORE if c.get("status") == status_filter]
        return {"count": len(filtered), "conflicts": filtered}
    return {"count": len(_CONFLICT_STORE), "conflicts": _CONFLICT_STORE}


@router.post("/scan")
async def scan_all_conflicts():
    """Run an automated conflict scan across all departmental repositories in unified data_repositories."""
    global _CONFLICT_STORE, _CONFLICT_COUNTER
    repo_dir = get_repo_dir()

    scanned = 0
    new_conflicts = []

    STANDARD_DEPTS = ["Operations", "Product", "Technical", "Sales", "Finance", "Governance_Risk"]

    for dept_name in STANDARD_DEPTS:
        dept_folder = repo_dir / dept_name
        if not dept_folder.exists() or not dept_folder.is_dir():
            continue

        for doc in dept_folder.glob("*.*"):
            if doc.is_file() and not doc.name.startswith("~") and not doc.name.startswith("."):
                scanned += 1
                results = check_conflicts(str(doc), user_department=dept_name)
                for r in results:
                    c_item = {
                        "id": _CONFLICT_COUNTER,
                        "source_file": doc.name,
                        "source_dept": dept_name,
                        "source_location": r.get("source_location", ""),
                        "source_chunk": r.get("source_chunk", ""),
                        "conflicting_file": r.get("conflicting_file", ""),
                        "conflicting_dept": r.get("conflicting_dept", ""),
                        "similarity": r.get("similarity", 0.0),
                        "conflict_type": r.get("conflict_type", "policy_conflict"),
                        "status": "active",
                    }
                    _CONFLICT_COUNTER += 1
                    _CONFLICT_STORE.append(c_item)
                    new_conflicts.append(c_item)

    return {
        "status": "scan_complete",
        "scanned_files": scanned,
        "new_conflicts_found": len(new_conflicts),
        "total_active_conflicts": len([c for c in _CONFLICT_STORE if c["status"] == "active"]),
    }


@router.post("/{conflict_id}/action")
async def take_conflict_action(conflict_id: int, payload: ConflictActionPayload):
    """Confirm impact or dismiss a detected conflict."""
    for item in _CONFLICT_STORE:
        if item["id"] == conflict_id:
            if payload.action == "confirm_impact":
                item["status"] = "impact_confirmed"
                item["notes"] = payload.notes or "Impact confirmed by governance officer."
            elif payload.action == "dismiss":
                item["status"] = "dismissed"
                item["notes"] = payload.notes or "Dismissed as false positive / acceptable divergence."
            elif payload.action == "reopen":
                item["status"] = "active"
                item["notes"] = ""
            else:
                raise HTTPException(status_code=400, detail="Invalid action. Use 'confirm_impact', 'dismiss', or 'reopen'.")
            return {"status": "ok", "conflict_id": conflict_id, "new_state": item["status"]}

    raise HTTPException(status_code=404, detail=f"Conflict ID {conflict_id} not found.")


@router.delete("/clear")
async def clear_conflicts():
    """Clear all conflict history."""
    global _CONFLICT_STORE
    _CONFLICT_STORE.clear()
    return {"status": "cleared"}
