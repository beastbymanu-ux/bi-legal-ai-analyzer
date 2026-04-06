"""
bi-legal-ai-analyzer — showcase_code.py
Key pipeline components for reference.
"""

# 1. Document ingestion and chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader

def ingest_contracts(pdf_paths: list[str]) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    docs = []
    for path in pdf_paths:
        loader = PyMuPDFLoader(path)
        pages = loader.load()
        docs.extend(splitter.split_documents(pages))
    return docs

# 2. Embed into ChromaDB
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def build_vector_store(docs, persist_dir="/data/chroma"):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    db.persist()
    return db

# 3. Query with local LLM (Ollama)
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

def query_contracts(question: str, db) -> str:
    llm = Ollama(model="llama3", base_url="http://localhost:11434")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever(search_kwargs={"k": 4}))
    return qa.run(question)

# 4. Nightly risk scanner
from datetime import date, datetime

def scan_risks(contracts: list[dict]) -> list[dict]:
    today = date.today()
    risks = []
    for c in contracts:
        expiry = datetime.strptime(c["expiry_date"], "%Y-%m-%d").date()
        days_left = (expiry - today).days
        if days_left < 30:
            risks.append({"contract": c["name"], "days_left": days_left, "severity": "critical"})
        elif days_left < 90:
            risks.append({"contract": c["name"], "days_left": days_left, "severity": "warning"})
    return risks
