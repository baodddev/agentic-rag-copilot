# Agentic RAG Copilot

An IT support assistant for a fictional company, Lumio Logistics. It answers employee questions from the company's private IT knowledge base, falls back to web search when the knowledge base has no answer, and shows which source it used and the steps it took.

## How it works

The agent is a LangGraph workflow:

1. **Route.** The LLM decides whether the question needs company knowledge (`kb`) or is small talk (`direct`).
2. **Retrieve and grade.** It pulls the top chunks from Pinecone and the LLM grades whether they answer the question.
3. **Fall back.** If the knowledge base is weak, it searches the web with Tavily and grades that evidence.
4. **Retry once.** If the web is also weak, it rewrites the query and tries the knowledge base again (`MAX_RETRIES`).
5. **Answer or stop.** It answers from the knowledge base or the web, or says there is not enough evidence.

Every answered question is logged to a local SQLite audit table (`data/audit.db`).

| Part | Tool |
|---|---|
| LLM | Groq (`openai/gpt-oss-120b` by default) |
| Embeddings | Pinecone Inference (`multilingual-e5-large`, 1024 dimensions) |
| Vector store | Pinecone serverless |
| Web search | Tavily |
| API and UI | FastAPI, a single-page chat UI in `templates/index.html` |

## Project layout

```
app/
  main.py              FastAPI app, serves the UI at /
  api/routes.py        /api/health, /api/chat, /api/ingest
  core/config.py       settings read from .env
  rag/workflow.py      the LangGraph agent
  rag/vectorstore.py   Pinecone index, embeddings, retriever
  services/ingestion.py  load and chunk .pdf, .txt, .md, .docx
  services/audit.py    SQLite audit log
data/sample_kb/        sample knowledge base (Markdown)
templates/index.html   chat UI
ingest_sample_kb.py    loads data/sample_kb into Pinecone
run.py                 starts the dev server (uvicorn with reload)
```

## Run it locally

### 1. Install

Python 3.11.

```bash
conda create -n project python=3.11 -y
conda activate project
pip install -r requirements.txt
```

### 2. Get API keys

All three have free tiers.

- **Groq:** https://console.groq.com/keys
- **Pinecone:** https://app.pinecone.io (API Keys)
- **Tavily:** https://app.tavily.com

### 3. Create `.env`

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-key
GROQ_MODEL=openai/gpt-oss-120b
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=fde-it-support-rag
PINECONE_NAMESPACE=company-it-kb
EMBEDDING_MODEL=multilingual-e5-large
TAVILY_API_KEY=your-tavily-key
ADMIN_API_KEY=pick-a-long-random-string
```

`.env` is in `.gitignore`. Never commit it.

### 4. Load the knowledge base

```bash
python ingest_sample_kb.py
```

The first run creates the Pinecone index. If an index with the same name but a different dimension already exists, **it is deleted and recreated**.

Run this once. Running it again adds the same chunks a second time; to reload the knowledge base, delete the namespace in the Pinecone console first.

### 5. Start the server

```bash
python run.py
```

- Chat UI: http://localhost:8000
- API docs: http://localhost:8000/docs

## API

**Ask a question**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

The response has `answer`, `source_used` (`private_kb`, `web_search`, `direct` or `insufficient_evidence`), `citations`, `trace` and `rewritten_query`.

**Add a document to the knowledge base** (`.pdf`, `.txt`, `.md`, `.docx`)

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "X-Admin-Key: <your ADMIN_API_KEY>" \
  -F "file=@path/to/document.pdf"
```

## Sample knowledge base

The documents in `data/sample_kb/` describe a fictional company and were written for this demo:

- `company_it_handbook.md`: VPN, passwords, MFA, software installation, lost laptops
- `service_desk_runbook.md`: email troubleshooting, slow laptops, ticket priority
- `security_policy.md`: phishing, data classification, USB devices, travel, incidents
- `onboarding_offboarding.md`: new hire accounts, laptops, access requests, leaving the company
- `workplace_tech_faq.md`: contacting the service desk, Wi-Fi, mobile email, printing, warehouse scanners, Teams rooms

Ask something outside these topics (for example, "How do I clear the DNS cache on Windows?") to see the web search fallback.
