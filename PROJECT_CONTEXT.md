# PROJECT_CONTEXT.md — Talk to Your Data

## Project Overview

This project is a conversational AI agent that allows non-technical users to query a PostgreSQL database using plain language via a Slack chat interface. Users can ask business questions in natural language — such as revenue comparisons, customer rankings, or trend analysis — and receive structured, readable answers without writing SQL or relying on pre-built dashboards.

**Target users:** Business users with no SQL knowledge who need on-demand data insights.

## System Scope

**In scope (Phase 1 — MVP):**
- Receiving natural-language queries from Slack
- Parsing and validating input (including guardrails to prevent access to personal data)
- Translating intent to SQL using PandasAI (>= 3)
- Executing queries against a PostgreSQL database via a semantic layer
- Synthesising and returning results to the user in Slack

**Out of scope (Phase 1):**
- Conversational memory / multi-turn context (planned for Phase 2)
- Visualisations or chart generation
- Write operations on the database
- Authentication / per-user access control beyond guardrails

## Architecture Summary

The system is composed of a **Main Agent** with three internal subsystems, plus two external dependencies:

| Subsystem | Role |
|---|---|
| **Intake** | Receives the raw Slack message, parses it, and applies guardrails (e.g. blocks queries involving personal data) |
| **Engine** | Core reasoning pipeline: understands intent → generates SQL via NLP-to-SQL → executes the query → synthesises a human-readable answer |
| **Output** | Formats the synthesised result and posts it back to Slack |

**External dependencies:**
- **Semantic layer** — provides a schema abstraction between the agent and the raw database, used by the NLP-to-SQL step and query execution. semantic layer must integrate smoothly with PandasAI to ensure that the generated SQL queries are valid and efficient.
- **PostgreSQL database** — the underlying data store queried at runtime

**Orchestration:** LangGraph manages the workflow between subsystems. PandasAI (>= 3) abstracts the NLP-to-SQL translation and query execution steps, potentially simplifying the Engine subsystem relative to the diagram.

**Interface:** A Slack bot handles all user-facing I/O (inbound messages and outbound responses).

## Key Inputs and Outputs

| | Description | Example |
|---|---|---|
| **Input** | Natural-language question from a Slack user | "Who are the top 5 customers by revenue last quarter?" |
| **Output** | Structured, readable answer posted in Slack | A ranked table or narrative summary |

## Design Rationale

- **PandasAI >= 3** is chosen to abstract NLP-to-SQL complexity, reducing the need for hand-crafted prompt engineering around SQL generation.
- **LangGraph** provides explicit, inspectable workflow orchestration — each step (intake → engine → output) is a discrete node, making the pipeline easier to debug and extend.
- **Semantic layer** decouples the agent from raw database schema, enabling business-friendly naming and hiding implementation details from the LLM.
- **Guardrails at intake** enforce data governance by blocking queries for personal data before any SQL is generated.
- **Slack as the interface** meets users where they already work, removing the need for a separate UI.
- **Phase 2 memory** will be added as a separate component (not yet in scope), enabling multi-turn conversations where users can refine or build on previous queries.