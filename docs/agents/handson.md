# Hands-on Agent Prompts

Use this prompt when asking an agent to work on a specific GitHub issue:

```text
Use the repo instructions in AGENTS.md and work on GitHub issue #<issue-number>.

First read the issue, labels, comments, CONTEXT.md, and any relevant ADRs/docs. Then implement the smallest complete vertical slice that satisfies the issue acceptance criteria. Prefer TDD when the issue changes behavior: write one failing behavior test, make it pass, and repeat.

Keep the implementation scoped to the issue. Do not introduce live web search, crawling, fabricated official sources, or unrelated refactors unless the issue explicitly asks for them. Follow the repo domain language and existing architecture decisions.

Before finishing, run the relevant verification commands. If all verifications pass, summarize the changes and tests. Then label the issue as done and close it with a short verification comment. If verification fails or the issue is incomplete, leave the issue open and explain exactly what remains.
```

For this repo, a completed issue means:

- The acceptance criteria are implemented.
- Relevant tests or verification commands pass.
- The issue has a final comment naming the verification command.
- The issue is labeled `done` and closed only after verification passes.
