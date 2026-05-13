# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root.
- **`docs/adr/`** for ADRs that touch the area you're about to work in.
- **`docs/architecture.md`** when the issue needs broader system shape beyond the domain glossary.

If these files don't exist yet, proceed silently. Don't block on them or ask for them upfront.

## File structure

Single-context repo:

```
/
├── CONTEXT.md
├── docs/architecture.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

## Use the glossary's vocabulary

When your output names a domain concept, use the term as defined in `CONTEXT.md`. Don't drift to synonyms the project explicitly avoids.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding it.
