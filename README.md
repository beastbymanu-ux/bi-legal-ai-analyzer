# Enterprise Legal AI: Private Contract Analysis & Compliance Hub

> Own project by Manu (OpenClaw Labs), built and tested with demo data. Not a client deployment.

> **On-premise contract intelligence** — LangChain · ChromaDB · Ollama/Llama3 · Streamlit · Docker

## Problem

Legal teams spending **40+ hrs/week** reviewing contracts manually. Junior staff using public ChatGPT — a direct GDPR violation risk. Missed penalty clauses causing recurring losses.

## Solution

On-premise contract intelligence system designed to run on a private VPS:

- **LangChain + PyMuPDF** chunks and embeds contracts into a private ChromaDB vector store
- **Ollama/Llama 3** answers natural language queries — zero data leaves the server
- **Nightly risk scanner** flags expiring contracts and high-severity clauses automatically
- **Streamlit dashboard** gives instant visibility to the entire legal corpus

## Architecture

```
PDF/DOCX Corpus → PyMuPDF + OCR → LangChain Chunking
→ ChromaDB (local) ←→ Ollama Llama3 (local)
→ Nightly Risk Scanner (cron) → Streamlit Dashboard → Nginx + SSL
```

## Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama / Llama 3 (local) |
| Vector DB | ChromaDB (on-premise) |
| Orchestration | LangChain |
| PDF Parsing | PyMuPDF + Tesseract OCR |
| API Layer | FastAPI |
| Dashboard | Streamlit |
| Infrastructure | Docker · Nginx · private VPS |

## Design principles

1. **Ownership** — Runs entirely on your own server. Zero cloud. GDPR-compliant by design.
2. **Scalability** — Dockerized. Add new document types or LLM models without vendor lock-in.

## Quick Start

```bash
git clone https://github.com/beastbymanu-ux/bi-legal-ai-analyzer
cd bi-legal-ai-analyzer
docker-compose up -d
# Visit http://localhost:8505
```
