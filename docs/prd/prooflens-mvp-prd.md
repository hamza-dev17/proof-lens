# PRD: ProofLens MVP

## Problem Statement

Students and everyday social media users receive suspicious screenshots, fake university announcements, scam internship posts, and urgent payment messages that are hard to verify quickly. They usually have to search official pages manually, compare scattered evidence, and decide whether the claim is trustworthy under time pressure.

ProofLens needs an MVP that turns a suspicious screenshot or pasted claim into a Turkish, evidence-backed Truth Report. The product must be convincing in a judge demo, but it must also be honest: verdicts are scoped to the Trusted Source Corpus and should not rely on model memory or live web search in v1.

## Solution

ProofLens will provide a Turkish-first verification dashboard where users choose a scenario, upload a screenshot or paste text, review extracted text, and receive a structured Truth Report. The report will show a conservative Overall Verdict, per-claim Verdicts, Confidence Levels, trusted source citations, Manipulation Signals, and recommended actions.

The MVP will support two Scenario Families:

- suspicious university announcements
- internship/job scam posts

The university lane will support the Regional University Set for Gaziantep. GIBTÜ is the complete demo path with deeper Official University Source coverage. Gaziantep University, Hasan Kalyoncu University, and SANKO University are lightweight source collections using university-wide Official University Sources only.

The internship/job scam lane is separate from the university lane and uses Scam Guidance Sources plus clearly marked synthetic employer/demo sources.

The judge-facing dashboard will use a dark MacBook-style minimal interface with a two-panel analyzer, screenshot preview, OCR review, progress timeline, summary strip, source badges, and compact claim cards.

## User Stories

1. As a student, I want to paste a suspicious university announcement, so that I can quickly check whether it is supported by official sources.
2. As a student, I want to upload a screenshot of a suspicious post, so that I do not have to retype the claim manually.
3. As a student, I want to review extracted screenshot text before analysis, so that OCR mistakes do not change the verification result.
4. As a student, I want to select the scenario family, so that the app searches the right evidence collection.
5. As a student, I want to select my university for university-related claims, so that evidence from another university does not affect the result.
6. As a GIBTÜ student, I want GIBTÜ claims to be checked against deeper official GIBTÜ sources, so that common campus rumors can be verified more reliably.
7. As a Gaziantep student from another university, I want lightweight support for my university, so that the app still gives scoped answers based on available official sources.
8. As a student, I want unsupported claims to be marked Doğrulanamadı instead of guessed, so that the app does not overclaim.
9. As a student, I want each extracted Checkable Claim shown separately, so that I can see which part of a suspicious message is true, false, misleading, or unverified.
10. As a student, I want a conservative Overall Verdict, so that I can get a quick answer before reading the full report.
11. As a student, I want Confidence Levels shown as simple Turkish labels, so that I understand reliability without fake precision.
12. As a student, I want official sources shown with title, owner, URL, trust level, and retrieval date, so that I can inspect the evidence myself.
13. As a student, I want source badges such as Resmi kaynak and GİBTÜ, so that I can quickly judge source quality.
14. As a student, I want supporting and contradicting evidence separated, so that the reasoning is easy to scan.
15. As a student, I want Manipulation Signals shown separately from Verdicts, so that suspicious wording does not get confused with proof.
16. As a student, I want warnings for urgent language, payment requests, anonymous authority, missing date, and no official source, so that I can recognize scam patterns.
17. As a student, I want recommended actions after the report, so that I know whether to pay, share, verify, or contact student affairs.
18. As a student, I want the app to tell me not to pay before verifying official sources, so that I avoid scam payments.
19. As a student, I want reports to be written in student-friendly Turkish, so that I can understand them quickly.
20. As a student, I want English terms in internship posts to be handled, so that mixed-language scam posts still produce Turkish reports.
21. As a judge, I want the first screen to be the actual analyzer, so that I immediately understand the product value.
22. As a judge, I want prepared demo cases, so that the presentation can show the product reliably.
23. As a judge, I want both text and screenshot demo paths, so that the team can demonstrate OCR and normal text verification.
24. As a judge, I want to see the verification process timeline, so that the multi-step workflow is visible without raw agent chatter.
25. As a judge, I want a polished dark MacBook-style dashboard, so that the MVP feels modern and competition-ready.
26. As a judge, I want a summary strip showing checked claims, sources scanned, and risk signals, so that I can understand the system's work in seconds.
27. As a judge, I want source citations to be visually prominent, so that I trust the verdict is evidence-backed.
28. As a judge, I want the app to avoid live web search in the demo, so that the result is deterministic and explainable.
29. As a developer, I want the Trusted Source Corpus to be manually curated in v1, so that demo evidence is stable and reviewable.
30. As a developer, I want source metadata to be validated, so that citations and retrieval filters stay reliable.
31. As a developer, I want source retrieval filtered by Scenario Family and selected university, so that evidence is not mixed across contexts.
32. As a developer, I want local multilingual embeddings for Turkish retrieval, so that source search works without another paid embedding API.
33. As a developer, I want LangGraph-style controlled workflow nodes, so that the verification path is structured and testable.
34. As a developer, I want typed backend tools for OCR, retrieval, source metadata, manipulation detection, and report saving, so that agents do not rely on model memory.
35. As a developer, I want the Skeptic step to allow one rewritten retrieval attempt, so that weak first retrievals can improve without making the workflow chaotic.
36. As a developer, I want UI-first structured JSON, so that the frontend can render claim cards without parsing raw agent messages.
37. As a developer, I want screenshot uploads treated as Temporary Uploads, so that privacy is easier to explain.
38. As a developer, I want no login in MVP, so that the demo stays focused on verification.
39. As a developer, I want optional Saved Reports only as structured data, so that demo history can exist without storing raw screenshots by default.
40. As a future maintainer, I want direct source insertion, crawling, PDF ingestion, accounts, and broader universities left for v2, so that v1 remains achievable.

## Implementation Decisions

- Build the MVP around the domain concepts in the glossary: Trusted Source Corpus, Truth Report, Scenario Family, Official University Source, Scam Guidance Source, Checkable Claim, Verdict, Confidence Level, Manipulation Signal, Extracted Text Review, Verification Timeline, Temporary Upload, and Saved Report.
- Use a seeded curated corpus for v1. The app must not search the live internet during verification.
- Build the Trusted Source Corpus from manually selected and cleaned sources.
- Use real Official University Sources for real universities, especially GIBTÜ.
- Do not fabricate official-looking GIBTÜ evidence.
- Use clearly marked synthetic/demo employer sources only for non-university internship scam examples.
- University sources must include only university websites, official announcements, academic calendars, regulations/directives, student affairs pages, career center pages, and official social media when linked from the university website.
- Student groups, unofficial social media pages, news summaries, unsourced screenshots, AI summaries, and forums are not official evidence.
- Support the Regional University Set: GIBTÜ, Gaziantep University, Hasan Kalyoncu University, and SANKO University.
- Make GIBTÜ the complete university demo path.
- Keep the other three universities lightweight and university-wide only.
- Keep the internship/job scam lane separate from the university lane.
- Use FastAPI for the backend and Next.js for the frontend.
- Use LangGraph-style controlled workflow nodes instead of free-form agent chat.
- Use Groq vision for image text extraction.
- Use Groq text reasoning for claim extraction, verification, skepticism, verdict generation, and report writing.
- Use local multilingual embeddings for Turkish retrieval.
- Use ChromaDB for the vector index.
- Use SQLite only for optional structured Saved Reports or demo history.
- Use typed tools available to workflow nodes: image text extraction, evidence retrieval, source metadata lookup, manipulation signal detection, and optional report saving.
- Restrict workflow tools to seeded corpus and backend services in v1.
- Allow the Skeptic step one additional retrieval attempt with a rewritten query when initial evidence is weak.
- Extract conservative Checkable Claims rather than every tiny detail.
- Use Verdict rules consistently:
  - Doğru means trusted evidence supports the claim.
  - Yanlış means trusted evidence directly contradicts the claim.
  - Yanıltıcı means partial truth, missing context, exaggeration, or unsupported implication.
  - Doğrulanamadı means trusted evidence is missing, insufficient, or inconclusive.
- Missing evidence should usually produce Doğrulanamadı, not Yanlış.
- Present Confidence Levels as Yüksek güven, Orta güven, and Düşük güven instead of exact percentages in the UI.
- Return UI-first structured JSON rather than raw agent messages.
- The response contract must support input type, scenario family, selected university, extracted text, overall verdict, overall confidence level, claim cards, source citations, manipulation signals, and recommended actions.
- Reports must always be generated in Turkish, even when input contains English wording.
- The frontend should start with the analyzer, not a marketing landing page.
- Use a dark MacBook-style judge-facing dashboard with a two-panel layout.
- Include scenario selector, university selector, upload area, paste area, screenshot preview, extracted text review, demo case shortcuts, verification timeline, final report, source rail, source badges, and recommended actions.
- Include three prepared Demo Cases:
  - fake GIBTÜ exam cancellation
  - fake GIBTÜ internship/payment announcement
  - internship scam post with registration fee
- Each Demo Case should have both a plain-text version and a screenshot version.
- Treat uploaded screenshots as Temporary Uploads and delete them after extraction and verification by default.
- Do not require login in MVP.
- Account-based saved history is v2.

The major modules to build are:

- Source Corpus module: validates source metadata, normalizes curated markdown content, chunks source text, and prepares documents for indexing.
- Retrieval module: indexes source chunks and retrieves evidence with scenario and university filters.
- Verification Workflow module: orchestrates OCR, claim extraction, retrieval, skepticism, verdict assignment, and report writing.
- Verdict Policy module: centralizes Verdict and Confidence Level rules so prompts and API behavior stay consistent.
- Manipulation Signal module: detects risk patterns independently from evidence verdicts.
- Report Contract module: defines the UI-first structured Truth Report response.
- Upload/OCR module: handles Temporary Uploads and extracted text review preparation.
- Saved Report module: optionally stores structured report JSON without saving raw screenshots by default.
- Frontend Analyzer module: implements the Turkish dark MacBook-style dashboard and report rendering.
- Demo Case module: provides fixed text and screenshot examples for presentation.

Deep module candidates:

- Retrieval module with a small public interface for indexed evidence lookup.
- Verdict Policy module with deterministic mapping from evidence state to verdict semantics.
- Report Contract module with schema validation.
- Source Corpus module with metadata validation and chunking.
- Manipulation Signal module with testable rule outputs.

## Testing Decisions

Good tests should verify external behavior and contracts, not implementation details. Tests should avoid depending on raw LLM phrasing when a stable schema or policy decision can be asserted instead.

Test these modules:

- Source Corpus module:
  - validates required metadata fields
  - rejects or flags missing trust level, source owner, URL, or retrieval date
  - distinguishes official, trusted guidance, and synthetic demo sources
- Retrieval module:
  - filters by Scenario Family
  - filters university evidence by selected university
  - never returns another university's evidence for a university-specific query
  - returns source metadata needed by citations
- Verdict Policy module:
  - direct contradiction maps to Yanlış
  - insufficient evidence maps to Doğrulanamadı
  - partial truth or missing context maps to Yanıltıcı
  - manipulation signals alone do not force Yanlış
- Manipulation Signal module:
  - detects urgent language
  - detects payment requests
  - detects anonymous authority
  - detects missing official source
  - keeps signals separate from evidence verdicts
- Report Contract module:
  - validates required top-level fields
  - validates claim card fields
  - validates source citation metadata
  - supports summary strip counts for checked claims, sources scanned, and risk signals
- Verification Workflow module:
  - produces a structured Truth Report from pasted text using seeded fixtures
  - allows one Skeptic retry when retrieval is weak
  - does not call live web search in v1
  - keeps reports Turkish
- Upload/OCR module:
  - accepts image input
  - produces editable extracted text
  - treats uploaded image as temporary
- Frontend Analyzer module:
  - renders scenario selection
  - renders university selector only when relevant
  - renders screenshot preview
  - renders extracted text review
  - renders progress timeline
  - renders overall verdict, claim cards, source badges, manipulation signals, and recommended actions
  - avoids exact confidence percentages in normal UI

Use fixture-based tests for the three Demo Cases. LLM-dependent behavior should be tested with deterministic stubs or recorded fixture responses where possible.

Prior art in the current repo is limited because the project is currently documentation-first. New tests should establish the first testing conventions for backend policy/retrieval modules and frontend rendering.

## Out of Scope

- Live internet search during verification
- Automatic crawling and source refresh
- Direct source insertion through a product admin UI
- Automatic PDF ingestion
- Login/accounts
- Multi-user saved report history
- Raw screenshot storage by default
- Broad university support outside Gaziantep
- Full support for arbitrary fact-checking outside the two MVP Scenario Families
- Faculty/department page support for the lightweight universities
- Treating Manipulation Signals as proof of falsity
- Exact confidence percentages in the normal Turkish UI
- Raw agent messages or chain-of-thought style text in the frontend

## Further Notes

The MVP should be built in the roadmap order already agreed:

1. Create curated source corpus files.
2. Seed source chunks into ChromaDB.
3. Build the FastAPI verification endpoint for pasted text.
4. Prepare the three fixed Demo Cases.
5. Add screenshot OCR and Extracted Text Review.
6. Build the Turkish Next.js interface.
7. Add optional Saved Report/history polish.

The strongest demo story is: ProofLens is not just an AI chatbot. It is a structured verification workspace that reads suspicious screenshots, checks trusted sources, separates evidence from risk signals, and gives Turkish students a clear action to take next.
