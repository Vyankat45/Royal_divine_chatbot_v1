# Royal Divine Chatbot

AI-powered chatbot for Royal Divine Produce Products LLP — an Indian exporter of dry fruits, spices, fruits, vegetables, and grains.

## Tech Stack

- **Backend**: FastAPI
- **Vector Store**: ChromaDB (with BAAI/bge-small-en-v1.5 embeddings)
- **LLM**: Groq (llama-3.3-70b-versatile)
- **Frontend**: Static HTML/CSS/JS
- **Lead Logging**: Google Sheets (optional)

## Local Development

```bash
# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Ingest website data into ChromaDB
python ingest.py

# Run the server
uvicorn main:app --reload
```

## Deploy on Render

### One-click Deploy

1. Push this repo to GitHub
2. In Render, create a **New Web Service**
3. Connect your GitHub repo
4. Use these settings:

| Setting | Value |
|---|---|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app` |
| **Health Check Path** | `/health` |

5. Add Environment Variables:

| Key | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GOOGLE_CREDENTIALS` | (Optional) Service account JSON for Google Sheets logging |

### Notes

- The `chroma_db/` directory contains pre-ingested vector data and is committed to the repo
- If you need to re-ingest data, run `python ingest.py` locally and commit the updated `chroma_db/`
- Google Sheets logging is optional — the app runs fine without it
- All product detection supports both English and Hindi/Marathi names with fuzzy matching

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key for Groq LLM |
| `GOOGLE_CREDENTIALS` | No | JSON string of Google service account for Sheets logging |

## Project Structure

```
├── main.py              # FastAPI app entry point
├── ingest.py            # Website scraper & ChromaDB ingestion
├── app/
│   ├── rag_service.py   # Core RAG + lead logic
│   ├── llm.py           # Groq LLM client
│   ├── vector_store.py  # ChromaDB interface
│   ├── embeddings.py    # HuggingFace embeddings
│   ├── product_detector.py  # Product detection with fuzzy matching
│   ├── lead_detector.py     # Purchase intent detection
│   ├── moq_checker.py       # MOQ validation
│   ├── contact_extractor.py # Email/phone/name extraction
│   ├── memory.py            # Conversation memory
│   ├── lead_memory.py       # Lead flow state
│   ├── products.py          # Product dictionary (EN/HI/MR)
│   ├── prompts.py           # System prompts
│   ├── guardrails.py        # Business question filtering
│   └── ...
├── static/
│   ├── index.html       # Landing page
│   ├── app.js           # Chat frontend
│   └── style.css        # Styles
└── chroma_db/           # Vector store (pre-built)
```
