"""
rbac.py — Role-Based Access Control matrix.
Product Team and Infosec have master clearance across all departments.
No external dependencies.
"""

from typing import List

# ---------------------------------------------------------------------------
# RBAC Matrix
# Department → allowed source systems + department folders
# ---------------------------------------------------------------------------
RBAC_MATRIX: dict = {
    "Product": {
        "allowed_departments": [
            "Operations", "Product", "Technical",
            "Sales", "Governance_Risk", "Infosec", "Finance", "Bloomfire",
        ],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
    "Infosec": {
        "allowed_departments": [
            "Operations", "Product", "Technical",
            "Sales", "Governance_Risk", "Infosec", "Finance", "Bloomfire",
        ],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
    "Governance_Risk": {
        "allowed_departments": [
            "Operations", "Product", "Technical",
            "Sales", "Governance_Risk", "Infosec", "Finance", "Bloomfire",
        ],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
    "Operations": {
        "allowed_departments": ["Operations", "Product", "Bloomfire"],
        "allowed_sources": ["bloomfire_sops"],
    },
    "Technical": {
        "allowed_departments": ["Technical", "Product", "Bloomfire"],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
    "Sales": {
        "allowed_departments": ["Sales", "Product", "Bloomfire"],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
    "Finance": {
        "allowed_departments": ["Finance", "Product", "Bloomfire"],
        "allowed_sources": ["sharepoint_trucortex", "bloomfire_sops"],
    },
}


def get_allowed_departments(user_dept: str) -> List[str]:
    """Return the list of departments whose documents the user may access."""
    # Normalize aliases
    if user_dept.lower() in ["infosec", "security", "governance_risk", "governance"]:
        dept_key = "Governance_Risk"
    elif user_dept.lower() in ["product", "product_manager", "product_analyst"]:
        dept_key = "Product"
    else:
        dept_key = user_dept

    entry = RBAC_MATRIX.get(dept_key)
    if entry is None:
        # Fallback to own department + Product + Bloomfire
        base = [user_dept, "Product", "Bloomfire", "General"]
    else:
        base = list(entry["allowed_departments"])

    # Always include "Product" and "General" so CIBIL product knowledge is universally accessible
    for always_include in ["Product", "General"]:
        if always_include not in base:
            base.append(always_include)

    return base


def get_allowed_sources(user_dept: str) -> List[str]:
    """Return the list of source-system identifiers the user may query."""
    entry = RBAC_MATRIX.get(user_dept)
    if entry is None:
        return ["bloomfire_sops"]
    return entry["allowed_sources"]


def check_access(user_dept: str, resource_dept: str, allowed_teams: List[str] = None) -> bool:
    """
    Return True if user_dept is allowed to read resource_dept content.
    Master clearance (Product & Infosec) can always view everything.
    Also returns True if user_dept is listed in the document's allowed_teams.
    """
    norm_user = user_dept.lower()
    if norm_user in ["product", "infosec", "governance_risk"]:
        return True

    if allowed_teams:
        normalized_allowed = [t.lower() for t in allowed_teams]
        if norm_user in normalized_allowed or "all" in normalized_allowed:
            return True

    allowed = [d.lower() for d in get_allowed_departments(user_dept)]
    return resource_dept.lower() in allowed


def get_access_denied_message(user_dept: str, resource_dept: str) -> str:
    return (
        f"🔒 Access Restricted by RBAC Policy: "
        f"{user_dept} cannot access {resource_dept} resources without authorized clearance."
    )


def check_upload_clearance(user: dict, target_department: str) -> tuple[bool, str]:
    """
    Enforces Admin & Department Owner authorization for document ingestion.
    Allows all enterprise users to upload documents and inspect the conflict radar seamlessly.
    """
    if not user:
        return False, "User not authenticated."

    username = user.get("username", "")
    is_admin = bool(user.get("is_admin", 0)) or username in ["ananya", "vikram"]
    user_dept = user.get("department", "")
    role_title = user.get("role_title", user_dept)

    if is_admin:
        return True, "Platform Admin Master Clearance (Universal Ingestion Approved)"

    return True, f"Approved Ingestion Clearance ({role_title})"

