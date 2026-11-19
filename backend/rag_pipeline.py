"""
ChromaDB RAG Pipeline with strict RBAC metadata filtering.
Includes automatic pure-Python vector fallback if chromadb/numpy wheels
are unavailable on newer Python versions (such as Python 3.14).
"""

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from document_parser import parse_file, SUPPORTED_EXTENSIONS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHROMA_PATH = str(Path(__file__).resolve().parent / "chroma_storage")
COLLECTION_NAME = "enterprise_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

STOP_WORDS = {
    "what", "is", "the", "a", "an", "and", "or", "in", "on", "of", "to", "for",
    "with", "tell", "me", "about", "how", "does", "explain", "are", "by", "from",
    "at", "it", "this", "that", "can", "you", "please", "we", "i", "do"
}

# ---------------------------------------------------------------------------
# Fallback Pure-Python Vector Store (for Python 3.14 / Missing C-Wheels)
# ---------------------------------------------------------------------------
class FallbackVectorCollection:
    """
    Lightweight, persistent vector store that mimics ChromaDB API.
    Computes TF-IDF cosine similarity vectors with persistent JSON storage.
    Supports where={"department": {"$in": [...]}} and {"$nin": [...]}.
    """
    def __init__(self, storage_path: str = CHROMA_PATH):
        self.storage_dir = Path(storage_path)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_file = self.storage_dir / "fallback_store.json"
        self.data: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if self.db_file.exists():
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def _save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _tokenize(self, text: str, filter_stops: bool = False) -> List[str]:
        words = [w.lower() for w in re.findall(r"\w+", text) if len(w) > 1]
        if filter_stops:
            filtered = [w for w in words if w not in STOP_WORDS]
            return filtered if filtered else words
        return words

    def _vectorize(self, text: str, is_query: bool = False) -> Dict[str, float]:
        tokens = self._tokenize(text, filter_stops=is_query)
        if not tokens:
            return {}
        counts = {}
        for t in tokens:
            # Give higher weight to non-stop words
            weight = 1.0 if t in STOP_WORDS else 2.5
            counts[t] = counts.get(t, 0.0) + weight
        length = math.sqrt(sum(v * v for v in counts.values()))
        return {k: v / length for k, v in counts.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        # Dot product of normalized term vectors
        common = set(vec1.keys()) & set(vec2.keys())
        return sum(vec1[k] * vec2[k] for k in common)

    def upsert(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        for cid, doc, meta in zip(ids, documents, metadatas):
            vec = self._vectorize(doc)
            self.data[cid] = {
                "id": cid,
                "document": doc,
                "metadata": meta,
                "vector": vec,
            }
        self._save()

    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, List]:
        if not query_texts:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        query_text = query_texts[0]
        q_vec = self._vectorize(query_text, is_query=True)
        query_keywords = set(self._tokenize(query_text, filter_stops=True))

        matches = []
        for item in self.data.values():
            meta = item["metadata"]

            # Evaluate where filter
            if where:
                dept_filter = where.get("department")
                if dept_filter:
                    if "$in" in dept_filter and meta.get("department") not in dept_filter["$in"]:
                        continue
                    if "$nin" in dept_filter and meta.get("department") in dept_filter["$nin"]:
                        continue

            sim = self._cosine_similarity(q_vec, item["vector"])

            # Boost exact keyword matches in filename or text
            doc_lower = item["document"].lower()
            fname_lower = meta.get("file_name", "").lower()
            keyword_hits = sum(1 for kw in query_keywords if kw in doc_lower or kw in fname_lower)
            if keyword_hits > 0:
                sim += 0.15 * keyword_hits

            if sim > 0.001:
                # ChromaDB distances in cosine space are: distance = 1 - similarity
                dist = max(0.0, 1.0 - min(1.0, sim))
                matches.append((dist, sim, item["document"], meta))

        matches.sort(key=lambda x: x[0])  # sort ascending distance
        top_matches = matches[:n_results]

        return {
            "documents": [[m[2] for m in top_matches]],
            "metadatas": [[m[3] for m in top_matches]],
            "distances": [[m[0] for m in top_matches]],
        }


# ---------------------------------------------------------------------------
# Collection Getter (ChromaDB or Fallback)
# ---------------------------------------------------------------------------
_collection_cache = None

def get_collection():
    """Return persistent ChromaDB collection or fallback store."""
    global _collection_cache
    if _collection_cache is not None:
        return _collection_cache

    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = None
        try:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            cand_ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
            # Test candidate embedding function
            _ = cand_ef(["test_probe"])
            ef = cand_ef
        except Exception:
            try:
                from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
                cand_ef = DefaultEmbeddingFunction()
                _ = cand_ef(["test_probe"])
                ef = cand_ef
            except Exception:
                ef = None

        if ef is None:
            # Native embeddings unavailable on this Python environment; use pure-Python TF-IDF vector collection
            print("[rag_pipeline] ChromaDB embedding models unavailable. Using FallbackVectorCollection.")
            fallback = FallbackVectorCollection(CHROMA_PATH)
            _collection_cache = fallback
            return fallback

        kwargs = {
            "name": COLLECTION_NAME,
            "metadata": {"hnsw:space": "cosine"},
            "embedding_function": ef,
        }

        collection = client.get_or_create_collection(**kwargs)
        _collection_cache = collection
        return collection
    except Exception as exc:
        print(f"[rag_pipeline] ChromaDB native engine unavailable ({exc}). Using FallbackVectorCollection.")
        fallback = FallbackVectorCollection(CHROMA_PATH)
        _collection_cache = fallback
        return fallback


def _make_chunk_id(file_path: str, page_or_slide: str, text: str) -> str:
    raw = f"{file_path}::{page_or_slide}::{text[:50]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
def ingest_chunks(chunks: list) -> int:
    if not chunks:
        return 0

    global _collection_cache
    collection = get_collection()
    ids, documents, metadatas = [], [], []

    for chunk in chunks:
        text = chunk["text"]
        meta = chunk["metadata"]
        chunk_id = _make_chunk_id(
            meta.get("file_path", ""),
            meta.get("page_or_slide", ""),
            text,
        )
        sanitized_meta = {
            k: (str(v) if v is not None else "") for k, v in meta.items()
        }
        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(sanitized_meta)

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        try:
            collection.upsert(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )
        except Exception as exc:
            print(f"[rag_pipeline] Upsert failed with native engine ({exc}). Switching to FallbackVectorCollection...")
            fallback = FallbackVectorCollection(CHROMA_PATH)
            _collection_cache = fallback
            fallback.upsert(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

    return len(ids)


def ingest_file(file_path: str, metadata_overrides: dict = {}) -> dict:
    try:
        chunks = parse_file(file_path, metadata_overrides)
        count = ingest_chunks(chunks)
        return {
            "file": file_path,
            "chunks_indexed": count,
            "status": "success",
        }
    except Exception as exc:
        return {
            "file": file_path,
            "chunks_indexed": 0,
            "status": "error",
            "error": str(exc),
        }


def ingest_all_repositories(base_path: str = "./data_repositories") -> dict:
    base = Path(base_path)
    if not base.exists():
        fallback_base = Path(__file__).resolve().parent.parent / "data_repositories"
        if fallback_base.exists():
            base = fallback_base
        else:
            return {
                "total_files": 0,
                "total_chunks": 0,
                "results": [],
                "errors": [],
                "message": f"Base path '{base_path}' does not exist.",
            }

    results = []
    errors = []
    total_chunks = 0

    for file in sorted(base.rglob("*")):
        if not file.is_file():
            continue
        # Skip temporary Office files (~$...) and hidden OS files
        if file.name.startswith("~") or file.name.startswith("."):
            continue
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        result = ingest_file(str(file))
        results.append(result)
        total_chunks += result.get("chunks_indexed", 0)
        if result["status"] == "error":
            errors.append(result["file"])

    return {
        "total_files": len(results),
        "total_chunks": total_chunks,
        "results": results,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Query & RBAC
# ---------------------------------------------------------------------------
_AUTO_INDEXED = False

def ensure_repositories_indexed():
    """
    Called on first query to ensure the vector store is populated.
    Uses collection.count() for an instant 0ms check.
    """
    global _AUTO_INDEXED
    if not _AUTO_INDEXED:
        _AUTO_INDEXED = True
        try:
            collection = get_collection()
            count = 0
            if hasattr(collection, "count"):
                try:
                    count = collection.count()
                except Exception:
                    count = len(getattr(collection, "data", {}))
            elif hasattr(collection, "data"):
                count = len(collection.data)

            if count == 0:
                print(f"[rag_pipeline] Vector collection empty (0 records), indexing repositories...")
                repo_dir = Path(__file__).resolve().parent.parent / "data_repositories"
                if not repo_dir.exists():
                    repo_dir = Path("D:/RAG/data_repositories")
                if repo_dir.exists():
                    ingest_all_repositories(str(repo_dir))
            else:
                print(f"[rag_pipeline] Vector collection verified ready with {count} chunks.")
        except Exception as e:
            print(f"[rag_pipeline] ensure_repositories_indexed notice: {e}")


def _get_allowed_departments(user_department: str) -> list:
    try:
        from rbac import get_allowed_departments
        return get_allowed_departments(user_department)
    except ImportError:
        return [user_department]


def query_rag(query: str, user_department: str, top_k: int = 5) -> dict:
    ensure_repositories_indexed()
    global _collection_cache
    collection = get_collection()
    allowed_departments = _get_allowed_departments(user_department)
    rbac_filtered = allowed_departments != []

    where_filter = {"department": {"$in": allowed_departments}}

    try:
        raw = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        print(f"[rag_pipeline] Query error with primary collection ({exc}). Trying FallbackVectorCollection...")
        fallback = FallbackVectorCollection(CHROMA_PATH)
        _collection_cache = fallback
        try:
            raw = fallback.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc2:
            return {
                "results": [],
                "rbac_filtered": rbac_filtered,
                "departments_searched": allowed_departments,
                "error": str(exc2),
            }

    results = []
    if raw and raw.get("documents") and raw["documents"][0]:
        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]

        for doc, meta, distance in zip(docs, metas, distances):
            score = max(0.0, 1.0 - distance)
            score_pct = f"{round(score * 100)}%"

            results.append({
                "text": doc,
                "score": round(score, 4),
                "score_pct": score_pct,
                "metadata": meta,
                "citation": {
                    "file_name": meta.get("file_name", ""),
                    "file_type": meta.get("file_type", ""),
                    "page_or_slide": meta.get("page_or_slide", ""),
                    "owner": meta.get("owner", ""),
                    "department": meta.get("department", ""),
                },
            })

    results.sort(key=lambda r: r["score"], reverse=True)

    return {
        "results": results,
        "rbac_filtered": rbac_filtered,
        "departments_searched": allowed_departments,
    }


# ---------------------------------------------------------------------------
# Synthesis (Claude-Grade Intelligent Synthesis with Qwen 2.5 3B GGUF)
# ---------------------------------------------------------------------------
def _clean_text(text: str, max_chars: int = 600) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + " …"
    return text


def synthesize_answer(query: str, results: list, user_department: str = "Product") -> str:
    """
    Synthesize answers using Qwen 2.5 3B GGUF via llama_cpp or Claude-grade structuring engine.
    Produces articulate, intelligent, structured answers directly grounded in the repository files.
    """
    try:
        from llm_engine import synthesize_claude_style
        return synthesize_claude_style(query, results, user_department)
    except Exception as exc:
        print(f"[rag_pipeline] Error in synthesize_claude_style ({exc}). Using direct fallback.")
        if not results:
            return "No relevant enterprise documents were found matching your query within your active clearance."
        top_results = results[:3]
        paragraphs = [r.get("text", "").strip() for r in top_results if r.get("text", "").strip()]
        return "\n\n".join(paragraphs)
