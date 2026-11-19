"""
routers/folders_router.py — Live Folder Tree Generator with Real RBAC Lock Status
Reflects physical disk state in ./data_repositories.
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from models import get_user
from rbac import get_allowed_departments, check_access
from document_parser import _infer_metadata_from_path, SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/folders", tags=["folders"])

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
    target = Path("D:/RAG/data_repositories")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _get_file_type(extension: str) -> str:
    ext_map = {
        ".pptx": "PPTX",
        ".docx": "DOCX",
        ".xlsx": "XLSX",
        ".pdf": "PDF",
        ".md": "MD",
        ".txt": "TXT",
    }
    return ext_map.get(extension.lower(), "FILE")


def _build_tree(directory: Path, allowed_depts: list, user_dept: str) -> list:
    items = []
    if not directory.exists():
        return items

    STANDARD_DEPTS = ["Operations", "Product", "Technical", "Sales", "Finance", "Governance_Risk"]

    # Gather files grouped by department across ALL repository folders
    dept_files_map = {d: [] for d in STANDARD_DEPTS}

    for f in sorted(directory.rglob("*"), key=lambda x: x.name.lower()):
        if f.is_file() and not f.name.startswith("~") and not f.name.startswith("."):
            if f.suffix.lower() in SUPPORTED_EXTENSIONS:
                meta = _infer_metadata_from_path(str(f))
                dept = meta.get("department", "Product")
                if dept in dept_files_map:
                    existing_names = [x.name for x in dept_files_map[dept]]
                    if f.name not in existing_names:
                        dept_files_map[dept].append(f)

    # Now construct the unified tree: ONE repository, 6 clean department vaults
    is_master = user_dept.lower() in ["product", "infosec", "governance_risk"]

    for dept in STANDARD_DEPTS:
        files = dept_files_map[dept]
        has_access = is_master or (dept in allowed_depts) or (user_dept == dept)

        file_children = []
        for entry in sorted(files, key=lambda x: x.name.lower()):
            ext = entry.suffix.lower()
            file_type = _get_file_type(ext)
            file_children.append({
                "name": entry.name,
                "type": "file",
                "file_type": file_type,
                "department": dept,
                "accessible": has_access,
                "size_bytes": entry.stat().st_size,
                "path": str(entry).replace("\\", "/"),
            })

        dept_dir = directory / dept
        items.append({
            "name": dept,
            "type": "folder",
            "department": dept,
            "accessible": has_access,
            "path": str(dept_dir).replace("\\", "/"),
            "children": file_children,
            "file_count": len(file_children),
        })

    return items


@router.get("/tree")
async def get_folder_tree(username: str = Query("alice")):
    """
    Return full folder tree for data_repositories tagged with
    the requesting user's RBAC accessibility flags.
    """
    user = get_user(username)
    if not user:
        user_dept = "Operations"
    else:
        user_dept = user["department"]

    allowed_depts = get_allowed_departments(user_dept)
    repo_dir = get_repo_dir()

    tree = _build_tree(repo_dir, allowed_depts, user_dept)

    return {
        "username": username,
        "department": user_dept,
        "allowed_departments": allowed_depts,
        "tree": tree,
    }
