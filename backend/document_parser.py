"""
Multi-format document parser.
Supports .pptx, .docx, .xlsx, .pdf, .md, and .txt files natively.
Includes fallback parsers using Python standard libraries (zipfile, xml.etree)
so parsing never fails even on pre-release Python environments.
"""

import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import List, Dict, Any

SUPPORTED_EXTENSIONS = {".pptx", ".docx", ".xlsx", ".pdf", ".md", ".txt"}


def _infer_metadata_from_path(file_path: str) -> dict:
    p = file_path.replace("\\", "/")
    parts = [s for s in p.split("/") if s]

    dept_map = {
        "operations": "Operations",
        "product": "Product",
        "technical": "Technical",
        "sales": "Sales",
        "finance": "Finance",
        "governance_risk": "Governance_Risk",
        "governance": "Governance_Risk",
        "risk": "Governance_Risk",
        "infosec": "Governance_Risk",
        "bloomfire": "Operations",
        "bloomfire_sops": "Operations",
        # Number-prefixed legacy folder mappings
        "1_operations_bloomfire": "Operations",
        "2_product": "Product",
        "3_technical": "Technical",
        "4_sales": "Sales",
        "5_governance_risk": "Governance_Risk",
        "6_finance": "Finance",
        # TransUnion CIBIL product folders -> Product
        "transunion_cibil_solutions_and_products": "Product",
        "1_solutions_suite": "Product",
        "2_featured_products_consumer_and_commercial": "Product",
        "3_featured_products_microfinance_and_financial_incl": "Product",
        "4_featured_products_fraud_identity_and_origination": "Product",
        "5_master_catalog_all_22_solutions_and_products": "Product",
        # SharePoint folders -> inherit their sub-dept
        "sharepoint_trucortex": "Product",
    }

    department = "Product"  # Default to Product (most files are CIBIL product docs)
    for part in reversed(parts[:-1]):  # scan parent folder names
        low = part.lower()
        if low in dept_map:
            department = dept_map[low]
            break
        # Handle number-prefixed folders like "3_Featured_Products_Microfinance_..."
        # by checking if it contains a known keyword
        for key, dept in dept_map.items():
            if low.startswith(key) or key in low:
                department = dept
                break

    return {"source_system": "Enterprise Repository", "department": department}


def _build_metadata(file_path: str, file_type: str, page_or_slide: str, metadata_overrides: dict) -> dict:
    inferred = _infer_metadata_from_path(file_path)
    base = {
        "file_name": Path(file_path).name,
        "file_type": file_type,
        "file_path": str(file_path),
        "page_or_slide": page_or_slide,
        "department": inferred["department"],
        "source_system": inferred["source_system"],
        "version": "1.0",
        "owner": "Enterprise Team",
        "status": "APPROVED",
    }
    base.update(metadata_overrides)
    base["file_name"] = Path(file_path).name
    base["file_path"] = str(file_path)
    base["file_type"] = file_type
    base["page_or_slide"] = page_or_slide
    return base


# ---------------------------------------------------------------------------
# DOCX Parser (Standard python-docx + zipfile fallback)
# ---------------------------------------------------------------------------
def parse_docx(file_path: str, metadata_overrides: dict = {}) -> list:
    chunks = []
    # 1. Try python-docx using safe document API (paragraphs & tables)
    try:
        from docx import Document
        doc = Document(file_path)
        current_section = "Overview"
        current_text: List[str] = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            style_name = getattr(p.style, "name", "").lower()
            if style_name.startswith("heading") or style_name.startswith("title"):
                if current_text:
                    chunks.append({
                        "text": "\n".join(current_text),
                        "metadata": _build_metadata(file_path, "DOCX", f"Section: {current_section}", metadata_overrides)
                    })
                    current_text = []
                current_section = text
            else:
                current_text.append(text)

        # Append table rows
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    current_text.append(" | ".join(cells))

        if current_text:
            chunks.append({
                "text": "\n".join(current_text),
                "metadata": _build_metadata(file_path, "DOCX", f"Section: {current_section}", metadata_overrides)
            })

        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] python-docx note: {exc}, using xml fallback.")

    # 2. Resilient OpenXML zipfile fallback
    try:
        with zipfile.ZipFile(file_path, "r") as z:
            xml_content = z.read("word/document.xml")
            root = ET.fromstring(xml_content)
            # Find all text elements <w:t>
            texts = []
            for elem in root.iter():
                if elem.tag.endswith("}t") and elem.text:
                    texts.append(elem.text.strip())
            joined = " ".join([t for t in texts if t])
            if joined:
                chunks.append({
                    "text": joined,
                    "metadata": _build_metadata(file_path, "DOCX", "Section: Document Content", metadata_overrides)
                })
                return chunks
    except Exception as exc:
        print(f"[document_parser] docx zip fallback failed: {exc}")

    return chunks


# ---------------------------------------------------------------------------
# PPTX Parser (python-pptx + zipfile fallback)
# ---------------------------------------------------------------------------
def parse_pptx(file_path: str, metadata_overrides: dict = {}) -> list:
    chunks = []
    try:
        from pptx import Presentation
        prs = Presentation(file_path)
        for idx, slide in enumerate(prs.slides, start=1):
            slide_texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        t = p.text.strip()
                        if t:
                            slide_texts.append(t)
                if shape.has_table:
                    for row in shape.table.rows:
                        row_vals = [c.text.strip() for c in row.cells if c.text.strip()]
                        if row_vals:
                            slide_texts.append(" | ".join(row_vals))
            try:
                if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                    nt = slide.notes_slide.notes_text_frame.text.strip()
                    if nt:
                        slide_texts.append(f"[Speaker Notes: {nt}]")
            except Exception:
                pass

            combined = "\n".join(slide_texts).strip()
            if combined:
                chunks.append({
                    "text": combined,
                    "metadata": _build_metadata(file_path, "PPTX", f"Slide {idx}", metadata_overrides)
                })
        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] python-pptx note: {exc}, using xml fallback.")

    # Fallback OpenXML pptx extraction
    try:
        with zipfile.ZipFile(file_path, "r") as z:
            slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
            for idx, sf in enumerate(sorted(slide_files), start=1):
                xml_data = z.read(sf)
                root = ET.fromstring(xml_data)
                texts = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("}t") and elem.text]
                combined = "\n".join([t for t in texts if t]).strip()
                if combined:
                    chunks.append({
                        "text": combined,
                        "metadata": _build_metadata(file_path, "PPTX", f"Slide {idx}", metadata_overrides)
                    })
        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] pptx zip fallback failed: {exc}")

    return chunks


# ---------------------------------------------------------------------------
# XLSX Parser (openpyxl + zipfile fallback)
# ---------------------------------------------------------------------------
def parse_xlsx(file_path: str, metadata_overrides: dict = {}) -> list:
    chunks = []
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue

            headers = [str(h).strip() if h is not None else f"Col{i+1}" for i, h in enumerate(rows[0])]
            for row_idx, row in enumerate(rows[1:], start=2):
                parts = []
                for col_idx, val in enumerate(row):
                    if val is not None and str(val).strip():
                        header = headers[col_idx] if col_idx < len(headers) else f"Col{col_idx+1}"
                        parts.append(f"{header}: {val}")
                if parts:
                    chunks.append({
                        "text": f"Sheet: {sheet_name} | " + " | ".join(parts),
                        "metadata": _build_metadata(file_path, "XLSX", f"Sheet: {sheet_name}, Row {row_idx}", metadata_overrides)
                    })
        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] openpyxl note: {exc}, using xml fallback.")

    # Fallback XML parsing
    try:
        with zipfile.ZipFile(file_path, "r") as z:
            sheet_files = [f for f in z.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
            for s_idx, sf in enumerate(sheet_files, start=1):
                xml_data = z.read(sf)
                root = ET.fromstring(xml_data)
                texts = [elem.text.strip() for elem in root.iter() if elem.tag.endswith("}t") and elem.text]
                if texts:
                    chunks.append({
                        "text": f"Sheet {s_idx} | " + " | ".join(texts),
                        "metadata": _build_metadata(file_path, "XLSX", f"Sheet: Data, Row {s_idx}", metadata_overrides)
                    })
        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] xlsx zip fallback failed: {exc}")

    return chunks


# ---------------------------------------------------------------------------
# PDF Parser (pypdf + stream fallback)
# ---------------------------------------------------------------------------
def parse_pdf(file_path: str, metadata_overrides: dict = {}) -> list:
    chunks = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                chunks.append({
                    "text": text,
                    "metadata": _build_metadata(file_path, "PDF", f"Page {page_idx}", metadata_overrides)
                })
        if chunks:
            return chunks
    except Exception as exc:
        print(f"[document_parser] pypdf note: {exc}, using stream fallback.")

    # Fallback PDF stream text extractor
    try:
        raw_bytes = Path(file_path).read_bytes()
        # Find BT ... ET streams
        matches = re.findall(rb"\((.*?)\)\s*Tj", raw_bytes)
        texts = [m.decode("utf-8", errors="ignore").strip() for m in matches if len(m) > 1]
        if texts:
            chunks.append({
                "text": "\n".join(texts),
                "metadata": _build_metadata(file_path, "PDF", "Page 1", metadata_overrides)
            })
            return chunks
    except Exception as exc:
        print(f"[document_parser] pdf stream fallback failed: {exc}")

    return chunks


# ---------------------------------------------------------------------------
# MD / TXT Parsers
# ---------------------------------------------------------------------------
def parse_md(file_path: str, metadata_overrides: dict = {}) -> list:
    content = Path(file_path).read_text(encoding="utf-8", errors="replace")
    chunks = []
    section_pattern = re.compile(r"^(#{1,2})\s+(.+)$", re.MULTILINE)
    matches = list(section_pattern.finditer(content))

    if not matches:
        text = content.strip()
        if text:
            chunks.append({
                "text": text,
                "metadata": _build_metadata(file_path, "MD", "Section: Document", metadata_overrides)
            })
        return chunks

    for i, match in enumerate(matches):
        header_text = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        full_text = f"{header_text}\n{body}".strip() if body else header_text
        if full_text:
            chunks.append({
                "text": full_text,
                "metadata": _build_metadata(file_path, "MD", f"Section: {header_text}", metadata_overrides)
            })

    return chunks


def parse_txt(file_path: str, metadata_overrides: dict = {}) -> list:
    content = Path(file_path).read_text(encoding="utf-8", errors="replace")
    paragraphs = re.split(r"\n{2,}", content)
    chunks = []
    for idx, p in enumerate(paragraphs, start=1):
        p = p.strip()
        if p:
            chunks.append({
                "text": p,
                "metadata": _build_metadata(file_path, "TXT", f"Para {idx}", metadata_overrides)
            })
    return chunks


# ---------------------------------------------------------------------------
# Main Dispatcher
# ---------------------------------------------------------------------------
def parse_file(file_path: str, metadata_overrides: dict = {}) -> list:
    ext = Path(file_path).suffix.lower()
    if ext == ".pptx":
        return parse_pptx(file_path, metadata_overrides)
    elif ext == ".docx":
        return parse_docx(file_path, metadata_overrides)
    elif ext == ".xlsx":
        return parse_xlsx(file_path, metadata_overrides)
    elif ext == ".pdf":
        return parse_pdf(file_path, metadata_overrides)
    elif ext == ".md":
        return parse_md(file_path, metadata_overrides)
    elif ext == ".txt":
        return parse_txt(file_path, metadata_overrides)
    else:
        # Generic text read
        try:
            return parse_txt(file_path, metadata_overrides)
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}")
