# ProofLens

ProofLens is a Turkish-first misinformation verification MVP. It turns suspicious screenshots or pasted claims into evidence-backed truth reports using a curated trusted source corpus, conservative verdict rules, and a FastAPI + Next.js interface.

The MVP focuses on two scenarios: suspicious university announcements and internship/job scam posts. Verdicts are scoped to indexed trusted sources; ProofLens is not designed as a general open-web fact checker.

## Tech Stack

- Backend: Python, FastAPI, LangGraph-style verification workflow
- Frontend: Next.js, React, TypeScript
- Evidence: curated Markdown sources under `trusted_sources/`
- Storage: SQLite for optional saved report history
- Testing: pytest for backend, Node test runner for frontend helpers

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn prooflens.api:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```

Run tests:

```powershell
pytest
cd frontend
npm test
```

## Project Structure

```text
prooflens/           Python backend, API, workflow, retrieval, reports
frontend/            Next.js app and frontend view-model helpers
trusted_sources/     Curated evidence corpus used for verification
fixtures/            Demo cases and stable sample data
tests/               Backend test suite
frontend/tests/      Frontend helper tests
docs/                Architecture notes, ADRs, UI notes, PRD
CONTEXT.md           Domain language and product rules
```

## Documentation

- `CONTEXT.md`: domain vocabulary and product rules
- `docs/architecture.md`: system design and implementation boundaries
- `docs/adr/`: architecture decision records
- `docs/prd/`: product requirements
- `AGENTS.md`: agent workflow instructions
