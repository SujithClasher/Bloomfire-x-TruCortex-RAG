"""
routers/upload_router.py — Live File Upload, Multi-Team RBAC Clearance,
AI Automatic Permission Suggestion, and Real-Time Conflict Radar Integration.
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel

from models import get_user
from rbac import check_access, check_upload_clearance
from rag_pipeline import ingest_file
from conflict_radar import check_conflicts
from routers.conflict_router import add_conflict_records

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".pptx", ".docx", ".xlsx", ".pdf", ".md", ".txt"}


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


@router.get("/clearance-status")
async def get_clearance_status(username: str, target_department: str = "Product"):
    """
    Check if a given persona holds upload authority as an approved Platform Admin
    or Department Owner for the target repository.
    """
    user = get_user(username)
    if not user:
        return {
            "authorized": False,
            "role_title": "Unauthenticated",
            "is_admin": False,
            "is_owner": False,
            "reason": "User not recognized."
        }

    is_allowed, reason = check_upload_clearance(user, target_department)
    return {
        "authorized": is_allowed,
        "username": username,
        "full_name": user.get("full_name", username),
        "department": user.get("department", ""),
        "role_title": user.get("role_title", user.get("department", "")),
        "is_admin": bool(user.get("is_admin", 0)),
        "is_owner": bool(user.get("is_owner", 0)),
        "clearance_type": "Platform Admin" if user.get("is_admin", 0) else ("Department Owner" if user.get("is_owner", 0) else "Analyst"),
        "reason": reason,
    }


class SuggestPermissionPayload(BaseModel):
    file_name: str
    target_department: Optional[str] = "Product"
    content_snippet: Optional[str] = ""


@router.post("/suggest-permissions")
async def suggest_permissions(payload: SuggestPermissionPayload):
    """
    AI Auto-Permission Suggestion Engine:
    Inspects document metadata, filename tokens, and content signals to
    automatically infer which teams should have view clearance.
    Eliminates manual guessing for enterprise team owners.
    """
    text = (f"{payload.file_name} {payload.content_snippet} {payload.target_department}").lower()

    # Rule 1: Technical specs / API Architecture
    if any(k in text for k in ["api", "endpoint", "architecture", "mtls", "schema", "gateway", "rest", "swagger", "json"]):
        return {
            "suggested_departments": ["Technical", "Product", "Infosec"],
            "primary_owner": "Technical",
            "sensitivity": "Engineering Confidential",
            "reason": "AI detected REST endpoints, gateway schemas, and transport security specs. Authorized for Technical, Product & Infosec audit."
        }

    # Rule 2: Pricing / Rate Cards / Billing
    if any(k in text for k in ["pricing", "rate_card", "rate card", "price", "billing", "discount", "fee", "tier", "commercial"]):
        return {
            "suggested_departments": ["Finance", "Sales", "Product"],
            "primary_owner": "Finance",
            "sensitivity": "Commercial Sensitive",
            "reason": "AI detected volume pricing matrices, discount structures, and billing tiers. Authorized for Finance, Sales & Product management."
        }

    # Rule 3: Sales Pitch / Commercial Enablement
    if any(k in text for k in ["pitch", "enablement", "deck", "slide", "quota", "gtm", "client"]):
        return {
            "suggested_departments": ["Sales", "Product"],
            "primary_owner": "Sales",
            "sensitivity": "Sales Enablement",
            "reason": "AI detected client presentation slides, pitch narrative, and SLA collateral. Authorized for Sales & Product."
        }

    # Rule 4: Security, PII, Compliance & Governance
    if any(k in text for k in ["pii", "pan", "aadhaar", "security", "retention", "compliance", "audit", "ciso", "fcra", "rbi"]):
        return {
            "suggested_departments": ["Infosec", "Product", "Operations"],
            "primary_owner": "Infosec",
            "sensitivity": "Restricted Compliance",
            "reason": "AI detected regulatory guidelines, identity security protocols, and data retention mandates. Authorized for Infosec, Product & Ops."
        }

    # Rule 5: Customer Disputes / Bloomfire SOPs
    if any(k in text for k in ["sop", "dispute", "resolution", "ticket", "adjudication", "workflow", "customer"]):
        return {
            "suggested_departments": ["Operations", "Product", "Sales", "Bloomfire"],
            "primary_owner": "Operations",
            "sensitivity": "Internal Operations",
            "reason": "AI detected dispute resolution SOPs, customer ticketing SLA, and turnaround guidelines. Authorized for Operations, Product & Sales."
        }

    # Default fallback: Product Team documents are organizational assets
    return {
        "suggested_departments": ["Product", "Operations", "Technical", "Sales", "Infosec"],
        "primary_owner": payload.target_department or "Product",
        "sensitivity": "Enterprise Standard",
        "reason": "AI classified document as general enterprise documentation. Clearance suggested across operational and technical stakeholders."
    }


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Form(...),
    target_department: str = Form(...),
    allowed_departments: Optional[str] = Form("ALL"),
):
    """
    Handle live file upload:
    1. Authenticate user; Product Team is Main (can upload across any department)
    2. Validate file format (.pptx, .docx, .xlsx, .pdf, .md, .txt)
    3. Save file into target enterprise repository directory on disk
    4. Ingest into ChromaDB with multi-team permission tags
    5. Run Change & Conflict Radar and register clashes into live radar store
    6. Return indexed count, permission matrix, and active conflicts
    """
    # 1. User & Admin/Owner clearance validation
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{username}' is not registered."
        )

    # Enforce Admin & Department Owner authorization
    is_allowed, reason = check_upload_clearance(user, target_department)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"🔒 {reason}"
        )

    # 2. File extension check
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 3. Determine save directory in unified single repository: data_repositories/<Department>
    base_repo = get_repo_dir()
    clean_dept = "Operations" if target_department.lower() == "bloomfire" else target_department
    dest_dir = base_repo / clean_dept

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    # Save to disk
    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    # 4. Immediate parsing and ChromaDB ingestion with custom allowed departments
    clean_allowed = allowed_departments if allowed_departments else "ALL"
    metadata_overrides = {
        "owner": user.get("full_name", username),
        "department": clean_dept,
        "allowed_departments": clean_allowed,
        "source_system": "Enterprise Repository",
        "status": "APPROVED",
        "version": "1.0",
    }

    ingest_result = ingest_file(str(dest_path), metadata_overrides=metadata_overrides)
    chunks_count = ingest_result.get("chunks_indexed", 0)

    # 5. Run Change & Conflict Radar against other departments (similarity > 0.65)
    raw_conflicts = check_conflicts(str(dest_path), user_department=target_department)

    # Register into live Radar Store so the drawer immediately reflects the conflict
    active_conflicts = add_conflict_records(raw_conflicts, file.filename, target_department)

    return {
        "status": "success",
        "message": f"Successfully parsed and indexed {chunks_count} chunks into ChromaDB.",
        "file_name": file.filename,
        "file_path": str(dest_path),
        "department": target_department,
        "allowed_departments": clean_allowed,
        "chunks_indexed": chunks_count,
        "conflicts_detected": len(active_conflicts),
        "conflicts": active_conflicts,
    }
