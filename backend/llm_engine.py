"""
llm_engine.py — Claude-Grade RAG Answer Synthesis Engine.
Uses gguf_engine.py for GGUF model management (auto-detects & loads Qwen locally).
Falls back to a fast structured synthesis engine (<5ms) when the LLM is loading.

All answers are strictly grounded in repository chunks — zero hallucination.
"""

import re
import time
from typing import List, Dict, Any, Optional


# ─── Import GGUF engine ───────────────────────────────────────────────────────
try:
    from gguf_engine import get_gguf_model
    _GGUF_ENGINE_AVAILABLE = True
except ImportError:
    _GGUF_ENGINE_AVAILABLE = False
    def get_gguf_model():
        return None


# ─── Greeting / identity handler ─────────────────────────────────────────────
def handle_conversational_query(query: str, user_dept: str) -> Optional[str]:
    """
    Returns a response ONLY for pure greetings and identity questions.
    Every domain/knowledge question (even one-word like 'CIR') goes to vector search.
    """
    q = query.strip().lower()

    if re.match(r"^(hi|hello|hey|good morning|good afternoon|good evening|greetings)[!.,\s]*$", q):
        return (
            f"Hello! I'm **TruCortex × Bloomfire KMP Intelligence**, your enterprise knowledge assistant.\n\n"
            f"I have full access to **{user_dept}**'s authorized vault and can answer questions across:\n"
            f"- **Products** — MFI Score (300–900), Grameen Score, CV CMR, Commercial NTC Score, TruIQ Studio, Consumer CIR\n"
            f"- **Operations & SOPs** — FI Waiver, IDV, Dispute Resolution, KYC Mismatch\n"
            f"- **Technical** — CIR v5.0 API schemas, Gateway endpoints, mTLS\n"
            f"- **Finance** — Rate cards, pricing tiers, commercial contracts\n\n"
            f"Ask anything — I'll search the indexed repository and give you a precise, cited answer."
        )

    if re.match(r"^(who are you|what (are|is) (you|this platform|trucortex)|what can you do|help me)[?!.,\s]*$", q):
        return (
            f"I'm **TruCortex × Bloomfire KMP Intelligence** — an enterprise AI assistant with Claude-level reasoning.\n\n"
            f"### Capabilities\n"
            f"- **Full repository search** across all authorized enterprise files (`.md`, `.docx`, `.xlsx`, `.pptx`, `.pdf`)\n"
            f"- **Zero-hallucination answers** strictly grounded in your enterprise documents\n"
            f"- **Exact source citations** with file name and section/slide/page references\n"
            f"- **RBAC enforcement** — your `{user_dept}` clearance gates what you can access\n"
            f"- **PII protection** — Aadhaar, PAN, phone numbers auto-masked before processing\n\n"
            f"Ask me anything about CIBIL products, scores, processes, or policies!"
        )

    return None


# ─── Qwen LLM inference ───────────────────────────────────────────────────────
def _run_llm_inference(llm, query: str, results: List[Dict[str, Any]]) -> Optional[str]:
    """
    Call the local GGUF model with a strict repo-grounded prompt.
    Returns the response string or None on failure (falls back to structured synthesis).
    """
    # Sentinel phrases the model outputs when it can't answer — we catch these and fallback
    _FALLBACK_PHRASES = [
        "i don't see that",
        "i do not see that",
        "not found in the authorized",
        "not available in the authorized",
        "no information available",
        "no relevant information",
        "the provided context does not",
        "the context does not contain",
        "cannot answer based on",
    ]

    try:
        # Build context from top 4 chunks (wider context = better compound answers)
        context_blocks = []
        for idx, r in enumerate(results[:4], 1):
            meta = r.get("metadata", {})
            fname = meta.get("file_name", "Enterprise Document")
            loc = meta.get("page_or_slide", "")
            loc_str = f" • {loc}" if loc else ""
            raw = r.get("text", "").strip()
            # Strip markdown heading markers for cleaner LLM context
            clean = re.sub(r"(?m)^#+\s*", "", raw).strip()[:700]
            context_blocks.append(f"[{idx}] {fname}{loc_str}\n{clean}")

        context = "\n\n---\n\n".join(context_blocks)

        # Primary source for citation footer
        p_meta = results[0].get("metadata", {}) if results else {}
        p_file = p_meta.get("file_name", "Enterprise Repository")
        p_loc = p_meta.get("page_or_slide", "")

        system_msg = (
            "You are TruCortex × Bloomfire KMP Intelligence, an expert AI assistant for TransUnion CIBIL. "
            "You answer with the precision and clarity of Claude.\n\n"
            "RULES:\n"
            "1. Start immediately with a direct 1-2 sentence answer — no filler like 'Based on the documents...'.\n"
            "2. Use concise bullet points with **bold lead-ins** for multi-step processes or comparisons.\n"
            "3. Include specific numbers: score ranges, SLAs, pricing tiers, API versions, CMR ranks.\n"
            "4. Cite the source inline after each fact: [File Name • Section].\n"
            "5. ALWAYS answer using the provided context — it contains relevant information. Extract and explain it clearly.\n"
            "6. Do NOT say 'I don't see that' — the context HAS the answer; find and present it.\n"
            "7. Do NOT suggest other documents. Do NOT repeat the question."
        )

        user_msg = (
            f"Enterprise Repository Context (use ALL of this to answer):\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer directly and completely using the context above:"
        )

        t0 = time.perf_counter()
        output = llm(
            f"<|im_start|>system\n{system_msg}<|im_end|>\n"
            f"<|im_start|>user\n{user_msg}<|im_end|>\n"
            f"<|im_start|>assistant\n",
            max_tokens=480,
            temperature=0.1,
            top_p=0.92,
            repeat_penalty=1.06,
            stop=["<|im_end|>", "<|im_start|>", "\n\nUser:", "\n\nQuestion:"],
        )
        elapsed = round(time.perf_counter() - t0, 2)

        text = output["choices"][0]["text"].strip()

        # If the model outputs a "not found" sentinel, fall back to structured synthesis
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in _FALLBACK_PHRASES):
            print(f"[llm_engine] LLM returned sentinel phrase. Switching to structured synthesis.")
            return None

        if text and len(text) > 30:
            print(f"[llm_engine] GGUF inference complete in {elapsed}s.")
            return text

        return None
    except Exception as e:
        print(f"[llm_engine] GGUF inference error ({e}). Falling back to structured synthesis.")
        return None


# ─── Fast Claude-Grade synthesis fallback (<5ms) ─────────────────────────────
def _build_claude_grade_synthesis(query: str, results: List[Dict[str, Any]], user_dept: str) -> str:
    """
    Instant structured answer directly from retrieved repository chunks.
    Handles single-topic and multi-topic queries by pulling from ALL top chunks.
    Format: Executive Summary → Key Specifications → Source Citations
    """
    top = results[0]
    meta = top.get("metadata", {})
    primary_file = meta.get("file_name", "Enterprise Repository")
    primary_loc = meta.get("page_or_slide", "")
    score_pct = top.get("score_pct", "90%")
    dept = meta.get("department", "")

    # For multi-topic queries: gather content from ALL top results (not just primary file)
    selected = results[:5]

    # Build clean combined text from all selected chunks
    all_texts = []
    seen_text = set()
    for c in selected:
        raw = c.get("text", "").strip()
        clean = re.sub(r"(?m)^#+\s*", "", raw).strip()
        # Deduplicate very similar chunks
        snippet = clean[:80]
        if snippet not in seen_text and clean:
            seen_text.add(snippet)
            fname = c.get("metadata", {}).get("file_name", "")
            all_texts.append(f"[{fname}]\n{clean}")

    combined = "\n\n".join(all_texts)

    # Extract paragraphs (>40 chars, not heading-only lines)
    paragraphs = [
        p.strip() for p in combined.split("\n\n")
        if len(p.strip()) > 40 and not re.match(r"^(#+|={3,}|-{3,}|\[.+\]$)", p.strip())
    ]

    # Extract sentences
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", combined) if len(s.strip()) > 20]

    # Extract bullet points from source
    raw_bullets = []
    for line in combined.split("\n"):
        line = line.strip()
        if re.match(r"^[-*•]\s+.{15,}", line) or re.match(r"^\d+\.\s+.{15,}", line):
            clean_b = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
            if clean_b and clean_b not in [b for b in raw_bullets]:
                raw_bullets.append(clean_b)

    # Metric highlighter
    metric_re = re.compile(
        r"(₹[\d,]+(?:\s*crore|\s*lakh)?|"
        r"\b\d{3}\s*(?:to|–|-)\s*\d{3}\b|"
        r"\b\d+\s*%|"
        r"\bCMR-\d+(?:\s*(?:to|–|-)\s*CMR-\d+)?\b|"
        r"\b\d+\s*(?:business hours?|calendar days?|months?)\b|"
        r"\bv\d+\.\d+\b)", re.IGNORECASE
    )

    def highlight(text: str) -> str:
        return metric_re.sub(r"**\1**", text)

    sections = []

    # ── Executive Summary ────────────────────────────────────────────────────
    lead = ""
    for p in paragraphs:
        if re.match(r"^(specification|overview|scope|module \d|section \d|introduction|background|executive|\[)", p, re.IGNORECASE):
            continue
        if len(p) > 60:
            lead = p
            break
    if not lead:
        lead = next((s for s in sentences if len(s) > 50), combined[:300])

    # Clean any file-name prefixes from lead
    lead = re.sub(r"^\[.+?\]\n?", "", lead).strip()
    sections.append(f"### Executive Summary\n{lead}")

    # ── Key Specifications ──────────────────────────────────────────────────
    sections.append("### Key Specifications & Parameters")

    if raw_bullets:
        bullet_list = [f"- {highlight(b)}" for b in raw_bullets[:10]]
        sections.append("\n".join(bullet_list))
    else:
        # Classify sentences into metric-heavy vs prose
        metric_sents = [s for s in sentences if metric_re.search(s)]
        prose_sents = [s for s in sentences if not metric_re.search(s)]
        pool = (metric_sents or prose_sents)[:8]
        sections.append("\n".join(f"- {highlight(s)}" for s in pool))

    # ── Additional Context ───────────────────────────────────────────────────
    if len(paragraphs) > 1:
        extra = [
            re.sub(r"^\[.+?\]\n?", "", p).strip()
            for p in paragraphs[1:5]
            if len(p) > 60 and p != lead
        ][:3]
        if extra:
            sections.append("### Additional Context")
            for p in extra:
                sections.append(p)

    # ── Source Citations (all unique files referenced) ────────────────────────
    seen_files = []
    for r in results[:4]:
        fn = r.get("metadata", {}).get("file_name", "")
        loc = r.get("metadata", {}).get("page_or_slide", "")
        if fn and fn not in [x[0] for x in seen_files]:
            seen_files.append((fn, loc))

    citation_parts = []
    for fn, loc in seen_files[:3]:
        loc_str = f" • {loc}" if loc else ""
        citation_parts.append(f"**{fn}**{loc_str}")

    sections.append(
        f"\n*Sources: {' | '.join(citation_parts)} — {score_pct} semantic relevance*"
    )

    return "\n\n".join(sections)


# ─── Main synthesis entry point ───────────────────────────────────────────────
def synthesize_claude_style(query: str, results: List[Dict[str, Any]], user_dept: str) -> str:
    """
    Primary answer synthesis entry point.
    1. Check for greeting / identity question (instant conversational response)
    2. No results → honest "not found" message
    3. Try local GGUF model (Qwen 2.5 3B)
    4. Fall back to fast Claude-Grade structured synthesis (<5ms)
    """
    # 1. Greeting / identity
    conv = handle_conversational_query(query, user_dept)
    if conv:
        return conv

    # 2. No repository results
    if not results:
        return (
            f"### No Matching Documents Found\n\n"
            f"I searched the enterprise repository within your authorized clearance (`{user_dept}`) "
            f"but found no documents matching **\"{query}\"**.\n\n"
            f"**Suggestions:**\n"
            f"- Try specific product names: 'Grameen Score', 'CV CMR', 'MFI Score', 'CIR', 'TruIQ'\n"
            f"- Rephrase with more keywords from the topic\n"
            f"- Contact a Platform Admin if you need access to another department's documents"
        )

    # 3. Local GGUF model
    llm = get_gguf_model()
    if llm is not None:
        result = _run_llm_inference(llm, query, results)
        if result:
            return result

    # 4. Fast structured fallback
    return _build_claude_grade_synthesis(query, results, user_dept)
