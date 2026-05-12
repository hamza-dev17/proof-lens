# Seeded Curated Corpus For V1

ProofLens v1 verifies claims only against a seeded curated source corpus instead of searching the live internet during analysis. This keeps the competition demo deterministic, makes citations inspectable, and prevents the app from presenting model memory or unstable web results as trusted evidence.

**Considered Options**

- Seeded curated corpus
- Live web search during verification
- Automatic crawler before each analysis

**Consequences**

- Verdicts are scoped to indexed sources, so missing evidence usually becomes `Dogrulanamadi`.
- Source crawling, refresh, and direct source insertion are v2 capabilities.
