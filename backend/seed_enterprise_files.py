"""
seed_enterprise_files.py
Ensures enterprise repository structure is active.
Does not generate artificial mock files if real repository files exist.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR / "data_repositories"

DEPT_DIRS = {
    "Operations": REPO_DIR / "Operations",
    "Product": REPO_DIR / "Product",
    "Technical": REPO_DIR / "Technical",
    "Sales": REPO_DIR / "Sales",
    "Governance_Risk": REPO_DIR / "Governance_Risk",
    "Finance": REPO_DIR / "Finance",
}


def unify_repositories():
    """Ensure all core department directories exist."""
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    for p in DEPT_DIRS.values():
        p.mkdir(parents=True, exist_ok=True)


def seed_all():
    """
    Validates enterprise repository structure.
    No hardcoded seed file generation - preserves actual disk repository files.
    """
    unify_repositories()
    file_count = sum(1 for f in REPO_DIR.rglob("*") if f.is_file() and not f.name.startswith("~"))
    print(f"[seed] Enterprise repository verified. Total files: {file_count} across {len(DEPT_DIRS)} department vaults.")


if __name__ == "__main__":
    seed_all()
