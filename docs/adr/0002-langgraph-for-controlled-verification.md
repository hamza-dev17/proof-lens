# LangGraph For Controlled Verification

ProofLens uses a LangGraph-style workflow for verification instead of a free-form multi-agent chat framework such as CrewAI. The product needs predictable steps, structured JSON, scoped tool calls, and conservative verdict behavior more than theatrical autonomous agents.

**Considered Options**

- LangGraph controlled workflow
- CrewAI-style role agents
- Single prompt chain

**Consequences**

- The presentation can still describe workflow roles such as Claim Extractor, Evidence Retriever, Skeptic, and Report Writer.
- Implementation should keep those roles as controlled nodes with typed inputs and outputs.
