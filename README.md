# Royal Divine Chatbot

AI-powered chatbot for **Royal Divine Produce Products LLP** — an Indian exporter of premium dry fruits, spices, fruits, vegetables, and grains, based in Mumbai.

**Live URL**: https://royal-divine-chatbot-v1-1.onrender.com

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Lead Collection Flow](#lead-collection-flow)
- [MOQ Rules](#moq-rules)
- [Product Detection](#product-detection)
- [Google Sheets Integration](#google-sheets-integration)
- [Deployment on Render](#deployment-on-render)
- [Local Development](#local-development)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Bugs Fixed](#bugs-fixed)
- [Known Issues & Future Improvements](#known-issues--future-improvements)

---

## Tech Stack

| Component | Technology | Version |
|---|---|---|
| **Backend Framework** | FastAPI | 0.136.3 |
| **LLM** | Groq (llama-3.3-70b-versatile) | via groq SDK 1.4.0 |
| **Vector Store** | ChromaDB | 1.5.9 |
| **Embeddings** | ONNX all-MiniLM-L6-v2 (via ChromaDB built-in) | 384 dims |
| **Fuzzy Matching** | rapidfuzz | 3.14.5 |
| **Frontend** | Static HTML + CSS + JS | — |
| **Lead Logging** | Google Sheets (gspread) | 6.2.1 |
| **Server** | uvicorn/gunicorn | 0.49.0 / 26.0.0 |
| **Python** | CPython | 3.12 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Render (Web Service)                  │
│                                                         │
│  ┌─────────────┐    ┌──────────────────────────────┐   │
│  │  uvicorn/    │───▶│        FastAPI App           │   │
│  │  gunicorn    │    │  (main.py)                    │   │
│  └─────────────┘    │  ├─ GET  /       → index.html │   │
│                     │  ├─ GET  /health → {"status"} │   │
│                     │  └─ POST /ask    → RAG answer  │   │
│                     └──────────┬───────────────────┘   │
│                                │                       │
│  ┌─────────────────────────────▼────────────────────┐  │
│  │              rag_service.py                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────┐   │  │
│  │  │ RAG Flow │ │Lead Flow │ │ Business Q&A   │   │  │
│  │  └────┬─────┘ └────┬─────┘ └───────┬────────┘   │  │
│  │       │            │               │             │  │
│  │  ┌────▼────┐  ┌────▼────┐   ┌──────▼──────┐    │  │
│  │  │ChromaDB│  │Google   │   │ Groq LLM    │    │  │
│  │  │(ONNX)  │  │Sheets   │   │(llama-3.3)  │    │  │
│  │  └────────┘  └─────────┘   └─────────────┘    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │              Static Frontend                    │  │
│  │  index.html → Landing page with stats          │  │
│  │  style.css  → Orange/cream theme               │  │
│  │  app.js     → Chat widget + inline form        │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## Features

### 1. RAG Pipeline
- Scrapes 39 pages from https://www.royaldivineproducts.com
- Stores in ChromaDB with metadata (product_name, category, business_type)
- Retrieves top 5 chunks for each query
- Falls back to business context (text) when no vector results found

### 2. Product Detection (with Conversation Context)
- Comprehensive dictionary of 200+ products with English + Hindi/Marathi names
- Fuzzy matching via rapidfuzz for misspellings
- Conversation history fallback (remembers last mentioned product)
- Top-3 suggestions when product not found

### 3. Step-by-Step Lead Collection (Inline in Chat)
- Detects purchase intent via keywords + phrases
- Collects: Product → Quantity → Country → Contact
- Validates MOQ after country is known
- Inline contact form inside chat widget (no modal popups)
- Submits to Google Sheets on completion

### 4. Smart Routing
- **Informational** → LLM with RAG context
- **Purchase intent** → Enter lead collection flow
- **Business question during lead flow** → LLM answers but keeps lead context
- **Cancel during lead flow** → Cleans up and returns to normal mode

### 5. Multi-Language Support
- LLM auto-detects input language
- Responds in same language (English, Hindi, Marathi, Arabic, French, etc.)

### 6. Google Sheets Logging
- Lead submissions → `Royal_divine_lead` sheet
- All conversations → `chatbot-logger` sheet
- Graceful failure if credentials missing (app still works)

### 7. Landing Page
- Professional hero section with stats (10+ years, 4000+ clients, 60+ countries, 5 categories)
- Product categories grid
- Floating chatbot FAB button
- Contact footer

---

## Project Structure

```
├── main.py                    # FastAPI entry point, routes, CORS, health endpoint
├── ingest.py                  # Scrapes website URLs → splits → embeds → stores in ChromaDB
├── requirements.txt           # Python dependencies (lightweight, no torch/CUDA)
├── pyproject.toml             # uv/pip project config with direct dependencies
├── uv.lock                    # Lock file (uv-managed)
├── .env                       # GROQ_API_KEY + GOOGLE_CREDENTIALS (gitignored)
├── .gitignore                 # Ignores .env, credentials.json, .venv, __pycache__
├── credentials.json           # Google service account credentials (gitignored)
├── README.md                  # This file
│
├── app/
│   ├── rag_service.py         # [CORE] Main orchestrator: RAG + Lead + Business flows
│   ├── llm.py                 # Groq client (llama-3.3-70b-versatile)
│   ├── embeddings.py          # ONNX MiniLM-L6-v2 embedding (no PyTorch!)
│   ├── vector_store.py        # ChromaDB interface (search, save)
│   ├── product_detector.py    # Product detection with fuzzy matching + history
│   ├── products.py            # 200+ product dictionary (EN/HI/MR names)
│   ├── lead_detector.py       # Purchase intent detection + quantity/country extraction
│   ├── lead_logger.py         # Google Sheets lead logging (lazy init, graceful fail)
│   ├── google_logger.py       # Google Sheets conversation logging (lazy init, graceful fail)
│   ├── moq_checker.py         # MOQ validation (India 1T, Export 5T)
│   ├── contact_extractor.py   # Email/phone/name regex extraction
│   ├── memory.py              # SessionMemory with TTL eviction (prevents OOM)
│   ├── lead_memory.py         # Lead flow state per session
│   ├── customer_memory.py     # Customer registration state
│   ├── guardrails.py          # Business question filtering (rejects off-topic)
│   ├── prompts.py             # System prompt for LLM
│   ├── business_context.py    # Static business info for fallback answers
│   ├── query_router.py        # Metadata filter builder for ChromaDB search
│   ├── loader.py              # Web scraping (WebBaseLoader)
│   ├── splitter.py            # Text splitting (RecursiveCharacterTextSplitter)
│   ├── cleaner.py             # HTML text cleaning
│   ├── metadata.py            # URL-based metadata generation
│   └── config.py              # User agent config
│
├── static/
│   ├── index.html             # Landing page with chatbot widget
│   ├── app.js                 # Chat frontend logic (send, receive, inline form)
│   └── style.css              # Styling (orange/cream theme)
│
├── api/
│   └── routes.py              # Alternative API router (currently unused)
│
└── chroma_db/                 # Pre-ingested vector store (committed to git)
    ├── chroma.sqlite3
    └── <uuid>/                # HNSW index files
```

---

## Lead Collection Flow

```
User: "I want to buy almonds"
  │
  ├─▶ is_lead() → True
  │
  ├─▶ detect_product("almonds") → "almonds"
  │
  ├─▶ Has quantity? → No → Ask quantity
  │     └─ Bot: "What quantity of Almonds?"
  │
  ├─ User: "5 tons"
  │     └─ Bot: "Which country?"
  │
  ├─ User: "UAE"
  │     └─ Check MOQ: 5 tons ≥ 5 tons (export) → Pass
  │     └─ Bot: "Please provide contact details"
  │
  ├─ User provides email + phone
  │     └─ save_lead() → Google Sheets
  │     └─ Bot: "Order Summary: Almonds, 5 tons, UAE"
  │
  └─ Done. Lead memory cleared.
```

### Cancel During Lead Flow
- Say "no", "cancel", "stop", "nevermind", "forget it", "leave it"
- Uses word-boundary regex: `\b(?:no\b(?!\w)|cancel|stop|...)` 
- Won't accidentally trigger on "notebook" or "denote"

### MOQ Failure During Lead Flow
- Lead memory is NOT deleted → user can retry with higher quantity
- Bot explains MOQ rules and asks for higher quantity

---

## MOQ Rules

| Destination | Minimum Order Quantity |
|---|---|
| **India** (domestic) | 1 Ton (1000 KG) |
| **Export** (all other countries) | 5 Tons (5000 KG) |

Enforced in `app/moq_checker.py`:
- Extracts numeric quantity + unit from user message
- Converts to KG (tons × 1000, grams ÷ 1000)
- Checks against threshold based on India vs export
- Called from `rag_service.py` after product + quantity + country are known

---

## Product Detection

**Dictionary** (`app/products.py`): 200+ entries covering:
- English names (almond, cashew, cumin, rice, mango, etc.)
- Hindi names (badam, kaju, jeera, chawal, aam, etc.)
- Marathi names (similar to Hindi with variations)

**Detection order** (`app/product_detector.py`):
1. Direct substring match (multi-word keys prioritized by length)
2. Fuzzy match on entire question (rapidfuzz partial_ratio, cutoff 85)
3. Token-level fuzzy match (ratio, cutoff 82, skips stop words)
4. Conversation history fallback (last mentioned product)
5. Top-3 suggestions when no match found

---

## Google Sheets Integration

### Sheets Used
| Sheet Name | Sheet ID | Data |
|---|---|---|
| `Royal_divine_lead` | `1gkOLcPMQKBkx-qx0TFkYTQlPwVCk4fKDUl-To9NMfSo` | Lead submissions |
| `chatbot-logger` | `1A7nYqog-ilXVXUuIqu_OsrIehA5GCF5jm7MOP87O9n4` | All conversations |

### Credentials
- Service account: `chatbot-logger@royal-divine-chat-logs.iam.gserviceaccount.com`
- Method 1: `credentials.json` file (locally)
- Method 2: `GOOGLE_CREDENTIALS` env var with JSON string (on Render)
- Both sheets must be shared with the service account email

### Lead Sheet Headers
`timestamp`, `session_id`, `name`, `email`, `phone`, `product`, `Quantity`, `country`, `Query`

### Conversation Sheet Data (no header row)
`timestamp`, `session_id`, `question`, `answer`

### Error Handling
Both `lead_logger.py` and `google_logger.py` use lazy initialization:
- Sheet connection is established on first use (not at import time)
- Failures are logged as warnings, never crash the app
- If credentials are missing, the app runs without logging

---

## Deployment on Render

### Settings

| Setting | Value |
|---|---|
| **Runtime** | Python 3 |
| **Region** | Any |
| **Branch** | `master` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app` |
| **Health Check Path** | `/health` |
| **Instance Type** | Free (512 MB RAM) — or paid for better performance |

### Environment Variables on Render

| Key | Value |
|---|---|
| `GROQ_API_KEY` | `gsk_...` (your Groq API key) |
| `GOOGLE_CREDENTIALS` | Full JSON string of service account credentials |

### Notes
- `chroma_db/` with pre-ingested vectors is committed to git — no scraping on Render
- Embedding model is ChromaDB's built-in ONNX MiniLM-L6-v2 — no PyTorch needed
- Build takes ~3-5 min (installs 100+ packages)
- Cold start takes ~20-30 sec (loads ONNX model + ChromaDB)
- Free tier has 512 MB RAM — sufficient for current usage

### Redeploying After Changes
```bash
git add .
git commit -m "description of changes"
git push
# Then in Render Dashboard: Manual Deploy → Deploy latest commit
```

---

## Local Development

```bash
# Prerequisites
uv python pin 3.12
git clone <repo>
cd ChatBot_RD

# Virtual environment
uv venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies (lightweight, no torch)
pip install -r requirements.txt

# OR use uv for faster installs:
uv pip install -r requirements.txt

# Environment variables
# Create .env file with:
#   GROQ_API_KEY=gsk_your_key_here
#   GOOGLE_CREDENTIALS={"type":"service_account",...}

# Run server (development with hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Open browser: http://localhost:8000
```

### Re-ingesting Website Data
```bash
# Delete old vector store
rm -rf chroma_db/

# Run ingestion (scrapes 39 pages, chunks, embeds, stores)
python ingest.py

# Expected output:
#   Loading documents...
#   Loaded 39 documents
#   Splitting documents...
#   Created 631 chunks
#   Saving to ChromaDB...
#   Ingestion Complete

# Commit the new chroma_db/
git add chroma_db/
git commit -m "Re-ingested website data"
git push
```

---

## API Endpoints

### `GET /`
Serves the landing page (`static/index.html`).

### `GET /health`
Health check for Render. Returns:
```json
{"status": "ok"}
```

### `POST /ask`
Main chat endpoint.

**Request:**
```json
{
  "question": "What dry fruits do you offer?",
  "session_id": "unique_session_id"
}
```

**Response (informational):**
```json
{
  "answer": "We offer the following dry fruits:\n• Almonds\n• Cashews\n..."
}
```

**Response (lead flow step):**
```json
{
  "answer": "What quantity of Almonds are you looking for?"
}
```

**Response (lead submitted):**
```json
{
  "answer": "Thank you!\n\nYour inquiry has been submitted successfully.\n\nOrder Summary:\n• Product: Almonds\n• Quantity: 5 tons\n• Country: UAE\n\nOur sales team will contact you shortly."
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | **Yes** | — | Groq API key for LLM access |
| `GOOGLE_CREDENTIALS` | No | — | Service account JSON string for Google Sheets |
| `HF_TOKEN` | No | — | HuggingFace token (avoids unauthenticated warning) |
| `PORT` | No | 8000 | Server port (set by Render automatically) |

---

## Bugs Fixed

This section documents the bugs discovered and fixed during development. Keep this for reference.

| # | Bug | File | Fix |
|---|---|---|---|
| 1 | **Cancel phrase `"no"` matched "notebook"** — substring `"no"` is in "notebook", "denote", "anonymous" | `rag_service.py:80-81` | Word-boundary regex: `\bno\b(?!\w)` |
| 2 | **Email/phone not accumulated** — user had to provide both email AND phone in a single message, impossible to provide one at a time | `rag_service.py:144-184` | Accumulate in `lead_memory` across turns, check stored values |
| 3 | **Unbounded memory growth** — `conversation_memory`, `lead_memory`, `customer_memory` were plain dicts with no eviction → OOM after sustained use | `memory.py`, `lead_memory.py`, `customer_memory.py` | Replaced with `SessionMemory` class: 24h TTL, 1000 session cap |
| 4 | **`is_lead()` false positives** — "What is the cost of almonds?" triggered lead flow because "cost" was a lead keyword | `lead_detector.py:62-76` | Added `INFORMATIONAL_PATTERNS` check: if query starts with "what/tell me/how much/do you" and has no quantity → not a lead |
| 5 | **Regex `\bk\b` matched "okay", "make"** — standalone `k` in quantity regex extracted "okay" as "ok" + "k" | `lead_detector.py:80-81` | Removed `k` from quantity unit regex |
| 6 | **Silent exception swallowing** — `ask_question` wrapped everything in bare `except Exception` with no logging | `rag_service.py:49-54` | Added `logger.exception()` before returning error message |
| 7 | **`lead_logger.py` crashed on import** — tried to connect to Google Sheets at module level, crashed if credentials missing | `lead_logger.py` | Refactored to lazy initialization with try/except (like `google_logger.py`) |
| 8 | **`requirements.txt` UTF-16 encoded** — couldn't be read on Linux/Render | `requirements.txt` | Converted to UTF-8, removed heavy torch/CUDA packages |
| 9 | **OOM on Render (512 MB)** — sentence-transformers + PyTorch used ~900 MB | `embeddings.py` | Switched to ChromaDB's built-in ONNX MiniLM-L6-V2 (no PyTorch) |
| 10 | **No CORS middleware** — cross-origin requests blocked | `main.py` | Added `CORSMiddleware` with allow-all |

---

## Known Issues & Future Improvements

### Current Limitations
1. **Conversation sheet has no header row** — `google_logger.py` appends rows without first creating headers
2. **Asymmetric MOQ handling** — New lead flow deletes `lead_memory` on MOQ failure (user must restart), but pending lead flow keeps it (user can retry). Intentional but inconsistent.
3. **No session expiry cleanup** — SessionMemory evicts stale sessions but doesn't proactively clean
4. **In-memory only** — All state (memory, leads, customers) is lost on server restart

### Recommended Improvements
1. **Add Redis/DB-backed persistence** — Replace in-memory SessionMemory with Redis or SQLite for persistence across restarts
2. **Add rate limiting** — Prevent abuse of `/ask` endpoint
3. **Add conversation export** — Allow downloading chat history
4. **Add feedback buttons** — Thumbs up/down on bot responses
5. **Improve product page scraping** — Some product pages may have incomplete metadata extraction in `metadata.py`
6. **Add unit tests** — Test lead flow, product detection, MOQ logic
7. **Upgrade to ChromaDB HTTP client** — Use a hosted ChromaDB instance for better scalability
8. **Add webhook notifications** — Notify sales team via email/Slack when a lead is submitted

---

## Google Sheets Service Account

The service account email that needs edit access to both sheets:
```
chatbot-logger@royal-divine-chat-logs.iam.gserviceaccount.com
```

If sheets stop receiving data:
1. Open each sheet
2. Share with the service account email above (Editor role)
3. Redeploy on Render

The credentials are stored in:
- Locally: `credentials.json` (gitignored)
- Render: `GOOGLE_CREDENTIALS` environment variable (JSON string)
