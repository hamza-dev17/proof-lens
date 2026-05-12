# FastAPI Backend And Next.js Frontend

ProofLens separates the system into a FastAPI backend and a Next.js frontend. FastAPI fits the Python-native verification stack around LangGraph, ChromaDB, local multilingual embeddings, and document ingestion, while Next.js stays focused on the Turkish user interface.

**Considered Options**

- FastAPI backend with Next.js frontend
- Next.js API routes for all backend work
- Streamlit-only MVP

**Consequences**

- The backend owns verification, retrieval, source ingestion, and report JSON.
- The frontend owns scenario selection, extracted text review, progress timeline, and claim-card rendering.
