"""
routers/document_viewer_router.py — In-app Document Preview & Inspection.
Enforces RBAC before serving file content and returns cleanly formatted
multi-format slides, sheets, sections, and pages for interactive UI viewing.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from models import get_user
from rbac import get_allowed_departments, check_access
from document_parser import parse_file, _infer_metadata_from_path

router = APIRouter(prefix="/documents", tags=["documents"])

def get_repo_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "data_repositories",
        Path(__file__).resolve().parent.parent / "data_repositories",
        Path("D:/RAG/data_repositories"),
        Path("./data_repositories").resolve(),
        Path("../data_repositories").resolve(),
    ]
    for c in candidates:
        if c.exists() and (c / "bloomfire_sops").exists() or (c / "Product").exists() if c.exists() else False:
            return c
    return Path("D:/RAG/data_repositories")


def _find_file(filename_or_path: str) -> Optional[Path]:
    """
    Find a file by exact path or by filename anywhere in the repository.
    Case-insensitive on Windows. Returns the FIRST match found.
    """
    p = Path(filename_or_path)
    # Absolute path provided
    if p.exists() and p.is_file():
        return p

    # Search recursively in repo
    repo_dir = Path("D:/RAG/data_repositories")
    if not repo_dir.exists():
        repo_dir = get_repo_dir()

    target_name = p.name.lower()
    for candidate in repo_dir.rglob("*"):
        if candidate.is_file() and candidate.name.lower() == target_name:
            return candidate

    return None


@router.get("/preview")
async def preview_document(
    file_path: str = Query(..., description="Path or name of the document"),
    username: str = Query(..., description="Active user for RBAC verification"),
    target_location: Optional[str] = Query(None, description="Optional slide/sheet/page to highlight"),
):
    """
    Return parsed structured preview of an enterprise document:
    - Enforces strict department RBAC
    - Returns structured chunks categorized by slide, sheet, page, or section
    """
    # 1. RBAC Verification
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{username}' is not authenticated."
        )

    user_dept = user["department"]
    allowed_depts = get_allowed_departments(user_dept)

    # 2. Locate File
    target_file = _find_file(file_path)
    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{file_path}' not found in enterprise repositories."
        )

    # 3. Determine File Department using unified path inference
    inferred_meta = _infer_metadata_from_path(str(target_file))
    file_dept = inferred_meta.get("department", "Product")

    # Check RBAC (Product Team & Infosec have Master Clearance across all documents)
    is_master = user_dept in ["Product", "Infosec", "Governance_Risk"]
    has_access = is_master or (file_dept in allowed_depts)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"🔒 Access Restricted by RBAC Policy: Users in {user_dept} cannot view {file_dept} documents."
        )

    # 4. Parse Document
    try:
        chunks = parse_file(str(target_file))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(exc)}"
        )

    # Format into viewable sections
    sections: List[Dict[str, Any]] = []
    file_type = target_file.suffix.replace(".", "").upper()

    for idx, c in enumerate(chunks, 1):
        loc = c["metadata"].get("page_or_slide", f"Section {idx}")
        is_highlighted = False
        if target_location and isinstance(target_location, str) and target_location.lower() in loc.lower():
            is_highlighted = True

        sections.append({
            "index": idx,
            "location": loc,
            "content": c["text"],
            "is_highlighted": is_highlighted,
        })

    return {
        "status": "success",
        "file_name": target_file.name,
        "file_type": file_type,
        "department": file_dept,
        "file_size_bytes": target_file.stat().st_size,
        "total_sections": len(sections),
        "sections": sections,
        "user_department": user_dept,
    }


@router.get("/download")
async def download_document(
    file_path: str = Query(..., description="Path or name of the document"),
    username: str = Query(..., description="Active user for RBAC verification"),
):
    """
    Download original enterprise file (.pptx, .docx, .xlsx, .pdf, .md).
    Enforces strict Department RBAC before serving file binary payload.
    """
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{username}' is not authenticated."
        )

    user_dept = user["department"]
    allowed_depts = get_allowed_departments(user_dept)

    target_file = _find_file(file_path)
    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{file_path}' not found."
        )

    inferred_meta = _infer_metadata_from_path(str(target_file))
    file_dept = inferred_meta.get("department", "Product")

    is_master = user_dept in ["Product", "Infosec", "Governance_Risk"]
    has_access = is_master or (file_dept in allowed_depts)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"🔒 Download Blocked by RBAC: Role '{user_dept}' cannot download '{file_dept}' documents."
        )

    return FileResponse(
        path=str(target_file),
        filename=target_file.name,
        media_type="application/octet-stream",
    )


@router.get("/raw")
async def raw_document(
    file_path: str = Query(..., description="Path or name of the document"),
    username: str = Query(..., description="Active user for RBAC verification"),
):
    """
    Serve raw document file inline for embedded browser viewing (e.g. PDF iframe).
    Enforces RBAC before streaming.
    """
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_dept = user["department"]
    allowed_depts = get_allowed_departments(user_dept)

    target_file = _find_file(file_path)
    if not target_file:
        raise HTTPException(status_code=404, detail="File not found")

    inferred_meta = _infer_metadata_from_path(str(target_file))
    file_dept = inferred_meta.get("department", "Product")

    is_master = user_dept in ["Product", "Infosec", "Governance_Risk"]
    has_access = is_master or (file_dept in allowed_depts)
    if not has_access:
        raise HTTPException(status_code=403, detail="RBAC Denied")

    media_type = "application/pdf" if target_file.suffix.lower() == ".pdf" else "application/octet-stream"
    headers = {"Content-Disposition": f'inline; filename="{target_file.name}"'}

    return FileResponse(
        path=str(target_file),
        media_type=media_type,
        headers=headers,
    )

