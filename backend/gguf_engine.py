"""
gguf_engine.py — Optimized local GGUF model loader for TruCortex x Bloomfire KMP.

Auto-detects .gguf files from:
  1. D:\\RAG\\backend\\models\\         (drop model here — preferred)
  2. C:\\Users\\<user>\\Downloads\\      (auto-scans for any *.gguf)
  3. D:\\RAG\\models\\

Auto-tunes hardware:
  - Intel i5 8th Gen / 4 physical cores → n_threads=4
  - 16 GB DDR4 RAM → n_ctx=1536, n_batch=512
  - GPU: auto-detects NVIDIA via nvidia-smi (n_gpu_layers=-1 if found, else 0)

Usage:
    from gguf_engine import get_gguf_model
    llm = get_gguf_model()   # returns Llama() singleton or None
"""

import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
except ImportError:
    _LLAMA_AVAILABLE = False

# ─── Singleton state ────────────────────────────────────────────────────────
_MODEL: Optional["Llama"] = None
_LOADING = False
_LOAD_LOCK = threading.Lock()
_RESOLVED_PATH: Optional[Path] = None


# ─── Hardware auto-tune ──────────────────────────────────────────────────────
def _detect_cpu_threads() -> int:
    """
    Use physical core count ÷ 2, min 2, max 6.
    On an Intel i5 8th Gen (4 cores / 8 threads) this gives 4.
    """
    logical = os.cpu_count() or 4
    return max(2, min(6, logical // 2))


def _detect_gpu_layers() -> int:
    """Return -1 (all layers on GPU) if nvidia-smi found, else 0 (CPU mode)."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"[gguf_engine] GPU detected: {result.stdout.strip().splitlines()[0]}")
            return -1  # offload all layers to GPU
    except Exception:
        pass
    return 0  # CPU mode


# ─── Model file discovery ────────────────────────────────────────────────────
def _find_gguf_path() -> Optional[Path]:
    """
    Scan candidate directories for any .gguf file.
    Priority: backend/models/ > Downloads/ > D:\\RAG\\models\\
    Prefers the smaller/faster q4 quantization over q5 if both present.
    """
    global _RESOLVED_PATH
    if _RESOLVED_PATH and _RESOLVED_PATH.exists():
        return _RESOLVED_PATH

    search_dirs = [
        Path(__file__).resolve().parent / "models",          # D:\RAG\backend\models\
        Path(os.path.expanduser(r"~\Downloads")),             # C:\Users\...\Downloads\
        Path(r"D:\RAG\models"),
        Path(r"D:\RAG"),
    ]

    candidates = []
    for d in search_dirs:
        if d.exists():
            for f in sorted(d.glob("*.gguf")):
                if f.is_file() and f.stat().st_size > 500_000_000:   # > 500 MB
                    candidates.append(f)
            if candidates:
                break   # stop at first directory with valid models

    if not candidates:
        return None

    # Prefer q4 (smaller, faster) over q5; prefer non-coder over coder
    def _rank(p: Path) -> tuple:
        name = p.name.lower()
        q_score = 1 if "q4" in name else (2 if "q5" in name else 3)
        is_coder = 1 if "coder" in name else 0
        return (q_score, is_coder)

    candidates.sort(key=_rank)
    _RESOLVED_PATH = candidates[0]
    return _RESOLVED_PATH


# ─── Singleton loader ────────────────────────────────────────────────────────
def get_gguf_model() -> Optional["Llama"]:
    """
    Return the loaded Llama singleton. Thread-safe.
    Returns None immediately if model is still loading (uses fast synthesis fallback).
    """
    global _MODEL, _LOADING

    if _MODEL is not None:
        return _MODEL

    if not _LLAMA_AVAILABLE:
        return None

    with _LOAD_LOCK:
        if _MODEL is not None:   # double-checked locking
            return _MODEL
        if _LOADING:
            return None          # loading in background — use fast fallback

        model_path = _find_gguf_path()
        if not model_path:
            print("[gguf_engine] No .gguf model file found. Using Claude-Grade synthesis fallback.")
            return None

        _LOADING = True

    # Load outside lock so other threads can still serve via fallback
    try:
        n_threads = _detect_cpu_threads()
        n_gpu_layers = _detect_gpu_layers()
        print(f"[gguf_engine] Loading model: {model_path.name}")
        print(f"[gguf_engine] Hardware config: n_threads={n_threads}, n_gpu_layers={n_gpu_layers}, n_ctx=1536, n_batch=512")

        llm = Llama(
            model_path=str(model_path),
            chat_format="chatml",
            n_ctx=1536,
            n_batch=512,
            n_threads=n_threads,
            n_threads_batch=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
        _MODEL = llm
        print(f"[gguf_engine] Model ready: {model_path.name}")
        return _MODEL
    except Exception as exc:
        print(f"[gguf_engine] Failed to load model ({exc}). Using Claude-Grade synthesis fallback.")
        return None
    finally:
        _LOADING = False


def preload_model_background():
    """Call this at startup to load the model in a background thread."""
    t = threading.Thread(target=get_gguf_model, daemon=True)
    t.start()
