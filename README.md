# ProofLens

ProofLens, şüpheli ekran görüntülerini veya metin tabanlı iddiaları analiz ederek güvenilir kaynaklarla karşılaştıran AI destekli bir doğrulama sistemidir.

---

# Sistem Mimarisi

```mermaid
flowchart TD

A[Kullanıcı Görsel veya Metin Yükler]
--> B[OCR / Vision İşlemi]

B --> C[Claim Extraction]

C --> D[Embedding Generation]

D --> E[RAG Retrieval]

E --> F[Trusted Source Araması]

F --> G[Evidence Collection]

G --> H[LLM Verification]

H --> I[Truth Report]

I --> J[Confidence Score]
I --> K[Reasoning]
I --> L[Evidence]
```

---

# Kullanıcı Akışı

```mermaid
flowchart TD

A[Görsel veya Metin Upload]
--> B[OCR ile Metin Çıkarma]

B --> C[Ana Claim Belirleme]

C --> D[Semantic Retrieval]

D --> E[Trusted Source Araması]

E --> F[Kanıt Toplama]

F --> G[AI Verification]

G --> H[Doğruluk Raporu]
```

---

# Örnek Verification Flow

```mermaid
flowchart TD

A[Fake Duyuru Görseli]
--> B[OCR Text Extraction]

B --> C[Claim Extraction]

C --> D[GIBTU finalleri iptal edildi]

D --> E[RAG Retrieval]

E --> F[Resmi Duyurular]

F --> G[Verification]

G --> H[Likely False]
```

---

# Tech Stack

## Frontend
- Next.js
- React
- TypeScript

## Backend
- Python
- FastAPI

## AI / Retrieval
- LangChain
- LangGraph-style workflow
- RAG pipeline
- OCR / Vision processing
- Embedding retrieval

## Storage
- SQLite
- Markdown knowledge base

## Testing
- pytest
- TDD workflow

---

# Geliştirme Workflow'um

```mermaid
flowchart TD

A[prd.md]
--> D[GitHub Issues]

B[architecture.md]
--> D

C[ui.md]
--> E[Prototype Workflow]

E --> F[Frontend Tasarımı]

F --> G[Final Design Commit]

D --> H[Issue-by-Issue Development]

H --> I[TDD Workflow]

I --> J[Review Workflow]

J --> K[Diagnosis Workflow]
```

---

# Projenin Amacı

ProofLens'in amacı:
- sahte duyuruları,
- scam iş / staj ilanlarını,
- yanlış bilgileri,
- manipüle edilmiş ekran görüntülerini

daha hızlı doğrulayabilen bir sistem oluşturmaktır.

Sistem, modelin kendi hafızasına güvenmek yerine evidence-based verification yaklaşımı kullanır.

---

# Quick Start

## Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn prooflens.api:app --reload
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Testler

```powershell
pytest

cd frontend
npm test
```
