# ProofLens

ProofLens is a misinformation verification product that turns suspicious screenshots or pasted claims into evidence-audited truth reports.

## Language

**Trusted Source Corpus**:
A curated set of documents that ProofLens is allowed to use as evidence for verification.
_Avoid_: open internet, model memory, general web knowledge

**Truth Report**:
A user-facing explanation of checked claims, evidence, verdicts, confidence, manipulation signals, and recommended actions.
_Avoid_: AI answer, fact-check output

**Demo Institution**:
An institution used in the MVP presentation scenario.
_Avoid_: ambiguous source identity

**Turkish User Experience**:
The product language, verdict labels, explanations, and recommended actions are written for Turkish-speaking users.
_Avoid_: English-first interface, translated afterthought

**Student-Friendly Turkish**:
Clear, direct Turkish that a university student can understand quickly without bureaucratic wording.
_Avoid_: formal official language, legalistic phrasing, academic jargon

**Demo Case**:
A prepared suspicious input used to demonstrate ProofLens reliably during presentation.
_Avoid_: improvised-only demo, unsupported random claim

**Verdict**:
The evidence-scoped label assigned to a checked claim.
_Avoid_: universal truth judgment, unsupported conclusion

**Confidence Level**:
A simple user-facing confidence label that communicates how strongly evidence supports a verdict.
_Avoid_: exact percentage in the main Turkish UI, fake precision

**Extracted Text Review**:
The step where a user checks and edits text read from an uploaded screenshot before verification begins.
_Avoid_: silent OCR, uneditable extraction, hidden vision output

**Verification Timeline**:
A short user-facing progress sequence that shows the verification stages without exposing internal agent reasoning.
_Avoid_: raw agent chatter, hidden long-running analysis

**Verification Workflow**:
The controlled backend process that extracts claims, retrieves evidence, challenges interpretations, assigns verdicts, and prepares the report.
_Avoid_: free-form agent chat, unstructured reasoning chain

**Temporary Upload**:
A user-provided screenshot kept only long enough to extract text and complete verification.
_Avoid_: permanent screenshot storage, account-bound upload archive

**Saved Report**:
A structured truth report kept for local demo history or future user access.
_Avoid_: saved raw screenshot, mandatory account record

**Manipulation Signal**:
A suspicious wording or presentation pattern that increases caution but does not by itself prove a claim false.
_Avoid_: evidence, verdict reason, proof of falsity

**Overall Verdict**:
A conservative summary label for the whole truth report, derived from claim verdicts and risk signals.
_Avoid_: replacing per-claim verdicts, overconfident summary

**Checkable Claim**:
A meaningful factual statement extracted from user input that can be compared against trusted evidence.
_Avoid_: tiny grammatical fragments, emotional wording, non-verifiable opinions

**Scenario Family**:
A supported category of suspicious content that ProofLens is intentionally optimized to verify.
_Avoid_: universal fact-checking, arbitrary claim verification

**Trusted Demo Source**:
A hand-written markdown document in the repository that represents an official source for a demo institution.
_Avoid_: hidden database-only source, live web page, model-generated evidence

**Official University Source**:
A real public GIBTÜ page or document used as trusted evidence for university-related claims.
_Avoid_: fabricated official-looking GIBTÜ source, unsourced claim, model memory

**Scam Guidance Source**:
A trusted public guidance document about scam patterns, used for internship/job scam risk analysis.
_Avoid_: rumor, forum anecdote, unsupported safety advice

**Curated Source Collection**:
The manually selected and cleaned set of trusted sources prepared before the MVP demo.
_Avoid_: automatic live crawl, unreviewed source ingestion

**Regional University Set**:
The supported Gaziantep university collection used by the MVP source corpus.
_Avoid_: single-university-only product framing, unsupported universities presented as complete

**GIBTÜ**:
The real Turkish university that the MVP university-announcement scenario is built around.
_Avoid_: treating GIBTÜ as fictional, fabricating official GIBTÜ evidence

## Relationships

- A **Truth Report** is based on evidence from the **Trusted Source Corpus**
- A **Trusted Source Corpus** contains one or more trusted documents
- ProofLens verdicts are scoped to the available **Trusted Source Corpus**
- MVP demo evidence is built from real official sources where the institution is real, and clearly marked synthetic sources where the example is fictional
- A **Truth Report** is presented through the **Turkish User Experience**
- The **Turkish User Experience** uses **Student-Friendly Turkish**
- ProofLens reports are written in Turkish even when the submitted claim contains English text
- The MVP supports two **Scenario Families**: suspicious university announcements and suspicious internship/job posts
- Claims outside the supported **Scenario Families** should usually produce a scoped **Unverified** result
- In v1, the **Trusted Source Corpus** combines **Official University Sources** for GIBTÜ with clearly marked synthetic/demo sources for non-university examples
- Directly adding sources through the product interface is a v2 capability
- The v1 university scenario is complete for **GIBTÜ** and lightweight for the other universities in the **Regional University Set**
- **GIBTÜ** trusted sources should cover student affairs, announcement archive, regulations, academic calendar, fees, and career/internship guidance where real official sources exist
- Fake/scam user inputs may be synthetic, but GIBTÜ evidence must come from **Official University Sources**
- Other universities in the **Regional University Set** use lightweight real official sources only
- The **Regional University Set** is GIBTÜ, Gaziantep University, Hasan Kalyoncu University, and SANKO University
- Lightweight universities in the **Regional University Set** use university-wide official sources only, not faculty or department pages
- The internship/job scam **Scenario Family** is separate from the **Regional University Set** and is framed for Turkish students generally
- The internship/job scam **Scenario Family** uses both **Scam Guidance Sources** and clearly marked synthetic employer/demo sources
- The v1 **Trusted Source Corpus** is built as a **Curated Source Collection**
- Automatic crawling and source refresh are v2 capabilities
- **Official University Sources** include university websites, official announcements, academic calendars, regulations/directives, student affairs pages, career center pages, and official social media only when linked from the university website
- Student groups, unofficial social media pages, news summaries, unsourced screenshots, AI summaries, and forums are not **Official University Sources**
- A **Verdict** should be **False** only when trusted evidence directly contradicts the claim
- A **Misleading** **Verdict** means trusted evidence shows partial truth, missing context, exaggeration, or unsupported implication
- Missing or insufficient trusted evidence should usually produce an **Unverified** **Verdict**, not **False**
- The Turkish UI presents **Confidence Levels** as low, medium, or high rather than exact percentages
- Screenshot inputs pass through **Extracted Text Review** before claim verification
- The Turkish UI shows a **Verification Timeline** while analysis runs
- The MVP **Verification Workflow** is implemented with LangGraph-style controlled steps
- User screenshots are treated as **Temporary Uploads** by default
- The MVP does not require user accounts or login
- Account-based saved history is a v2 capability
- **Manipulation Signals** are shown separately from evidence-based **Verdicts**
- A **Truth Report** includes both per-claim **Verdicts** and a conservative **Overall Verdict**
- The **Verification Workflow** extracts conservative **Checkable Claims** instead of splitting every small detail
- The MVP presentation uses three **Demo Cases** plus optional free input

## Example Dialogue

> **Dev:** "Can ProofLens mark a claim false because the model already knows it is false?"
> **Domain expert:** "No. In the MVP, ProofLens can only justify verdicts using the **Trusted Source Corpus**."

## Flagged Ambiguities

- "trusted docs" means **Trusted Source Corpus**, not arbitrary web pages discovered during verification.
- "university" in MVP examples means **GIBTÜ** unless explicitly marked as a synthetic/example institution.
- "GIBTÜ" refers to the user's real university, so official-looking evidence must not be fabricated as if it came from GIBTÜ.
