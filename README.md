# 🧠 TruCortex × Bloomfire KMP Intelligence Platform

A production-grade, local enterprise RAG platform for **TransUnion CIBIL Intelligence** featuring a **Multi-Format Folder-to-Vector-DB RAG Pipeline (ChromaDB)** that natively parses `.pptx` (PowerPoint), `.docx` (Word), `.xlsx` (Excel), `.pdf`, and `.md` files — with strict **Department RBAC Metadata Filtering**, **Live Folder Sync & Upload**, **Real Regex PII GuardLLM**, and an interactive **Change & Conflict Radar**, powered by a local **Qwen 2.5 3B GGUF** model (`llama-cpp-python`) with auto GPU offloading (NVIDIA MX250 / CUDA) and Claude-style structured synthesis.

---

## 🌟 Key Architecture Pillars

```
┌────────────────────────────────────────────────────────────────────────┐
│               Vue 3 + Quasar Frontend (Port 5173)                      │
│   ┌──────────────────────┬──────────────────────┬──────────────────┐   │
│   │  Repository Explorer │  RAG Chat & Trace    │  Conflict Radar  │   │
│   │  (RBAC Lock Icons)   │  (                   │  & Audit Log     │   │
│   │                      │   Clickable Citations│                  │   │
│   └──────────────────────┴──────────────────────┴──────────────────┘   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API / Axios (Port 8010)
┌───────────────────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (Port 8010)                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 1. Ping / IDMart RBAC Auth Resolution                            │  │
│  │ 2. GuardLLM Input: Regex PAN & Aadhaar Blocking / Phone Masking  │  │
│  │ 3. Orchestrator Route: Department Policy Gatekeeper               │  │
│  │ 4. Vector Search: ChromaDB where={"department": {"$in": scopes}} │  │
│  │ 5. Qwen 2.5 3B GGUF Inference / Claude-Grade Synthesis           │  │
│  │ 6. GuardLLM Output: Extractive Grounded Synthesis & Masking      │  │
│  │ 7. Audit Trail: SQLite Zero-PII Log & Thumbs Up/Down Feedback    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                   │                                    │
│   ┌───────────────────────────────┴──────────────────────────────┐     │
│   ▼                               ▼                              ▼     │
│ ┌─────────────────────────┐  ┌─────────────────────────┐  ┌──────────┐ │
│ │ Multi-Format Parsers    │  │ ChromaDB Vector DB      │  │ SQLite   │ │
│ │ .pptx .docx .xlsx       │  │ (all-MiniLM-L6-v2)      │  │ (app.db) │ │
│ │ .pdf .md .txt           │  │ 190 Chunks / 33 Files   │  │ RBAC     │ │
│ └─────────────────────────┘  └─────────────────────────┘  └──────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
d:\RAG\
├── README.md                           # Comprehensive documentation & walkthrough
├── run_backend.bat                     # Windows one-click backend runner
├── run_frontend.bat                    # Windows one-click frontend runner
│
├── backend\
│   ├── main.py                         # FastAPI startup, lifecycle auto-seed & indexing
│   ├── requirements.txt                # Python dependencies
│   ├── models.py                       # SQLite schema: users, audit_log, feedback
│   ├── rbac.py                         # Department RBAC matrix & policy checks
│   ├── guard_llm.py                    # Regex PII detection (PAN, Aadhaar, Phone, Email)
│   ├── audit.py                        # Audit logging wrapper
│   ├── document_parser.py              # Native parsers: pptx, docx, xlsx, pdf, md, txt
│   ├── rag_pipeline.py                 # ChromaDB persistent vector ingestion & search
│   ├── conflict_radar.py               # Semantic cross-department similarity (>0.65)
│   ├── seed_enterprise_files.py        # Programmatic binary generator for demo files
│   │
│   └── routers\
│       ├── __init__.py
│       ├── query_router.py             # 6-step orchestrator chat endpoint
│       ├── upload_router.py            # Live file upload & immediate ChromaDB index
│       ├── folders_router.py           # Live folder tree with RBAC lock statuses
│       ├── conflict_router.py          # Radar conflict list & action handlers
│       ├── audit_router.py             # Zero-PII logs & user feedback endpoints
│       └── sync_router.py              # Live folder sync & ChromaDB re-index
│
├── frontend\
│   ├── package.json                    # Vue 3, Quasar, Pinia, Axios, Vite
│   ├── vite.config.ts                  # Vite config with Quasar plugin & proxy
│   ├── tsconfig.json                   # TypeScript config
│   ├── index.html                      # HTML entry
│   │
│   └── src\
│       ├── main.ts                     # Quasar + Pinia initialization
│       ├── App.vue                     # Root component
│       ├── boot\
│       │   └── axios.ts                # Axios client targeting http://localhost:8000
│       ├── css\
│       │   ├── app.scss                # Custom styling
│       │   └── quasar-variables.scss   # Quasar color tokens
│       ├── stores\
│       │   ├── auth.ts                 # User persona & department state
│       │   ├── chat.ts                 # Chat messages, trace, citations
│       │   ├── folders.ts              # Repository folder tree state
│       │   ├── conflicts.ts            # Conflict radar items & actions
│       │   └── audit.ts                # Audit trail & feedback state
│       ├── layouts\
│       │   └── MainLayout.vue          # Quasar layout with header & drawers
│       ├── pages\
│       │   └── ChatPage.vue            # Chat interface with quick prompt pills
│       └── components\
│           ├── UserSwitcher.vue        # Dropdown to switch across 6 department roles
│           ├── PipelineTrace.vue       # 6-step execution pill row with latency
│           ├── CitationChip.vue        # Clickable format-badge citation chips
│           ├── RepositoryDrawer.vue    # Left drawer with folder tree & lock icons
│           ├── UploadModal.vue         # Modal for file upload & immediate indexing
│           ├── ConflictRadarDrawer.vue # Radar showing cross-department clashes
│           └── AuditLogDrawer.vue      # Zero-PII audit trail & thumbs up/down
│
└── data_repositories\                  # Enterprise Document Folders
    ├── bloomfire_sops\
    │   ├── Customer_Dispute_Resolution_SOP.docx
    │   ├── KYC_Mismatch_Handling_Guide.pdf
    │   └── Bureau_Record_Correction_SOP.md
    └── sharepoint_trucortex\
        ├── Product\
        │   ├── CV_CMR_Overview_v3.2_APPROVED.pptx
        │   └── Internal_Score_Methodology_CONFIDENTIAL.docx
        ├── Technical\
        │   ├── CIR_v5.0_API_Schema_and_Release_Spec.pdf
        │   └── API_Gateway_Endpoints.xlsx
        ├── Sales\
        │   └── CV_CMR_Enterprise_Pitch_v2.1_APPROVED.pptx
        ├── Governance_Risk\
        │   └── Data_Retention_and_Approval_Policy_2026.docx
        └── Finance\
            └── Bureau_Pricing_and_Rate_Card_v4.xlsx
```

---

## ⚡ Quick Start & Run Commands

### 1. Start Backend (Terminal 1)
```bash
cd d:\RAG\backend

# Create & activate virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (auto-seeds files and ChromaDB on startup!)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs on `http://localhost:8000` (API docs at `http://localhost:8000/docs`).*

### 2. Start Frontend (Terminal 2)
```bash
cd d:\RAG\frontend

# Install frontend dependencies
npm install

# Start Vite dev server
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

---

## 🛡️ Department RBAC Policy Matrix

| Persona | Username | Department | Accessible Department Repositories |
|---|---|---|---|
| Alice Johnson | `alice` | **Operations** | `bloomfire_sops` (all SOPs) |
| Bob Smith | `bob` | **Product** | `Product` + `bloomfire_sops` |
| Charlie Brown | `charlie` | **Technical** | `Technical` + `bloomfire_sops` |
| Diana Prince | `diana` | **Sales** | `Sales` + `bloomfire_sops` |
| Eve Adams | `eve` | **Governance_Risk**| **ALL** departments (Enterprise Wide) |
| Frank Castle | `frank` | **Finance** | `Finance` + `bloomfire_sops` |

### RBAC Enforcement in Action
When logged in as **Diana (Sales)**:
- In the **Repository Explorer Drawer**, folders for `Product`, `Technical`, and `Finance` display **🔒 Red Lock Icons** with strikethroughs and tooltips: `"Access Restricted: Your role cannot view Technical files"`.
- If Diana asks: `"What are the internal API Gateway endpoints and auth headers?"`, retrieval is blocked at **Step 3 (Orchestrator Route)** with:
  > `🔒 Access Restricted by RBAC Policy: Sales cannot access Technical folders or resources.`

---

## 📡 6-Step Orchestrator Pipeline Trace

Every response generates a live step-by-step trace visible directly in the UI:

1. **`1. Ping/IDMart RBAC`**: Resolves user token, role (`Sales`), and allowed vector partitions (`['Sales', 'Bloomfire']`).
2. **`2. GuardLLM Input`**: Scans input with regular expressions:
   - Blocks PAN: `[A-Z]{5}[0-9]{4}[A-Z]` ➔ **HTTP 422 Unprocessable Entity** (stops before vector search).
   - Blocks 12-digit numbers (Aadhaar) ➔ **HTTP 422**.
   - Masks Phone numbers ➔ `[PHONE_MASKED]`.
   - Masks Emails ➔ `[EMAIL_MASKED]`.
3. **`3. Orchestrator Route`**: Inspects target topic against role matrix. Halts unauthorized departmental cross-queries.
4. **`4. Vector Search`**: Queries persistent ChromaDB with strict vector metadata filter:
   `collection.query(where={"department": {"$in": allowed_departments}})`
5. **`5. GuardLLM Output`**: Grounded extractive synthesis formats top-k retrieved chunks into clean Markdown and validates outbound PII scrub.
6. **`6. Audit Log`**: Stores zero-PII sanitized interaction in SQLite `audit_log` table and generates a unique audit reference ID.

---

## ⚠️ Change & Conflict Radar

When a file is uploaded or modified, or when clicking **"Scan Repositories"** in the Conflict Radar drawer:
- The system parses the document into chunks.
- Queries ChromaDB across all **other** department repositories.
- Any match exceeding **0.65 cosine similarity** is flagged as a potential conflict:
  - **Version Mismatch** (similarity > 0.90)
  - **Policy Divergence** (keywords: policy, retention, compliance, prohibited)
  - **Data Metric Clash** (divergent pricing or volume tiers)
- The user can review the comparison and click:
  - `✅ Confirm Impact` (Marks impact confirmed for compliance review)
  - `❌ Dismiss` (Dismisses divergence as false positive / acceptable)

---

## 🧪 Demonstration & Test Scenarios

Try these quick test scenarios in the chat UI:

| Test Scenario | Active User | Input Prompt | Expected Behavior |
|---|---|---|---|
| **RBAC Allowed Query** | `charlie` (Technical) | *"What are the internal API Gateway endpoints and rate limits?"* | ✅ Returns top chunks from `API_Gateway_Endpoints.xlsx` with citation chip. |
| **RBAC Blocked Query** | `diana` (Sales) | *"What are the internal API Gateway endpoints and rate limits?"* | 🔒 Blocked at Step 3: `"Access Restricted by RBAC Policy: Sales cannot access Technical folders"`. |
| **Product Methodology** | `bob` (Product) | *"Explain the internal TruCortex score methodology and feature weights."* | ✅ Retrieves confidential weights from `Internal_Score_Methodology_CONFIDENTIAL.docx`. |
| **Product Methodology** | `diana` (Sales) | *"Explain the internal TruCortex score methodology and feature weights."* | 🔒 Blocked by RBAC policy gatekeeper. |
| **Cross-SOP Query** | `alice` (Operations) | *"What is the step-by-step SOP for customer dispute resolution?"* | ✅ Retrieves 4-step workflow from `Customer_Dispute_Resolution_SOP.docx`. |
| **PAN Leak Interception** | Any User | *"Check status for customer PAN ABCDE1234F and update bureau."* | 🛑 **HTTP 422 GuardLLM Interception**: Stops before vector search, logs security block. |
| **Aadhaar Leak Interception**| Any User | *"Verify KYC mismatch for Aadhaar number 8923 4512 7890."* | 🛑 **HTTP 422 GuardLLM Interception**: Stops before vector search. |
| **PII Soft Masking** | Any User | *"Email report to john.doe@trucortex.com or call +91 9876543210."* | 🛡️ Phone and email masked to `[PHONE_MASKED]` and `[EMAIL_MASKED]`, query proceeds. |
| **Live File Upload** | `eve` or Dept Owner | Upload `.pptx` or `.docx` in the Upload Modal | 📦 File saved to disk, parsed, ingested to ChromaDB, and evaluated by Conflict Radar. |
| **Thumbs Up/Down** | Any User | Open Audit Log Drawer and click 👍 or 👎 on any row | 📋 Persists grounded evaluation into SQLite `feedback` table. |

---

## 🔒 Zero External Dependencies Guarantee
- **No OpenAI, Anthropic, or external LLM API calls.**
- **No external API keys required.**
- **Embeddings run locally** via `all-MiniLM-L6-v2` (`sentence-transformers`).
- **Synthesis is 100% grounded and extractive**, preventing hallucinations and unauthorized information leaks.

