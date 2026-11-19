"""
Semantic cross-check for newly uploaded/modified files.
Compares new file's chunks against ALL other departments' chunks in ChromaDB.
Flags conflicts where cosine similarity > 0.65.
"""

from document_parser import parse_file
from rag_pipeline import get_collection, _make_chunk_id

# Similarity threshold above which we flag a conflict
CONFLICT_THRESHOLD = 0.65

# Departments that are excluded from cross-department conflict scanning
_SKIP_DEPARTMENTS = {"Bloomfire"}


def _classify_conflict(score: float, source_text: str, conflict_text: str) -> str:
    """
    Heuristic classification of the conflict type based on similarity and content signals.
    """
    source_lower = source_text.lower()
    conflict_lower = conflict_text.lower()

    # Version mismatch: very high similarity (nearly identical) but different docs
    if score >= 0.90:
        return "version_mismatch"

    # Policy conflict: legal / policy keywords present
    policy_keywords = {"policy", "procedure", "compliance", "regulation", "must", "shall", "prohibited"}
    if any(kw in source_lower for kw in policy_keywords) or any(kw in conflict_lower for kw in policy_keywords):
        return "policy_conflict"

    # Data overlap: numbers, dates, pricing, percentages
    import re
    data_pattern = re.compile(r"(\$[\d,]+|\d+%|\b\d{4}-\d{2}-\d{2}\b|\bQ[1-4]\b)")
    if data_pattern.search(source_text) or data_pattern.search(conflict_text):
        return "data_overlap"

    return "data_overlap"


def check_conflicts(file_path: str, user_department: str) -> list:
    """
    Parse the given file and compare each chunk against all other departments' content
    in ChromaDB. Returns a list of conflict dicts for chunks whose similarity exceeds
    CONFLICT_THRESHOLD.

    Args:
        file_path: Path to the new or updated file.
        user_department: Department that owns the file (excluded from comparison set).

    Returns:
        List of conflict dicts:
        {
            "source_chunk": str,
            "source_location": str,
            "conflicting_chunk": str,
            "conflicting_file": str,
            "conflicting_dept": str,
            "similarity": float,
            "conflict_type": str,
        }
    """
    # Parse the incoming file
    try:
        chunks = parse_file(file_path)
    except Exception as exc:
        return [
            {
                "source_chunk": "",
                "source_location": "N/A",
                "conflicting_chunk": "",
                "conflicting_file": "",
                "conflicting_dept": "",
                "similarity": 0.0,
                "conflict_type": "error",
                "error": str(exc),
            }
        ]

    if not chunks:
        return []

    collection = get_collection()

    # Build the exclusion list: skip the uploader's department + Bloomfire
    excluded_departments = list(_SKIP_DEPARTMENTS | {user_department})

    conflicts = []

    for chunk in chunks:
        source_text = chunk["text"].strip()
        source_location = chunk["metadata"].get("page_or_slide", "")

        if not source_text:
            continue

        # Query other departments (use $nin to exclude uploader's dept + Bloomfire)
        try:
            raw = collection.query(
                query_texts=[source_text],
                n_results=3,
                where={"department": {"$nin": excluded_departments}},
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            # ChromaDB raises when no results match the filter — skip silently
            continue

        if not (raw and raw.get("documents") and raw["documents"][0]):
            continue

        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]

        for doc, meta, distance in zip(docs, metas, distances):
            # Cosine distance → similarity (ChromaDB cosine space: distance ∈ [0,2])
            similarity = round(max(0.0, 1.0 - distance), 4)

            if similarity < CONFLICT_THRESHOLD:
                continue

            conflict_type = _classify_conflict(similarity, source_text, doc)
            conf_dept = meta.get("department", "Enterprise")
            conf_file = meta.get("file_name", "Vault File")
            conf_loc = meta.get("page_or_slide", "Vault Section")

            conflicts.append(
                {
                    "source_chunk": source_text[:500],
                    "source_location": source_location or "Uploaded Section",
                    "conflicting_chunk": doc[:500],
                    "conflicting_file": conf_file,
                    "conflicting_dept": conf_dept,
                    "conflicting_location": conf_loc,
                    "discrepancy_summary": f"Cross-vault overlap between {user_department} and {conf_dept} ({conf_file}) with {int(similarity * 100)}% semantic correlation.",
                    "similarity": similarity,
                    "conflict_type": conflict_type,
                }
            )

    return conflicts
