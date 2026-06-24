# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`talk_to_your_data` is a Slack-based AI agent that lets non-technical users query a PostgreSQL database in plain language — no SQL required. Users ask questions like "who are the top 5 customers by revenue last quarter?" and receive structured answers directly in Slack.

See `PROJECT_CONTEXT.md` for full scope, architecture diagram, and design rationale.

## Commands

```bash
uv sync                      # install dependencies (preferred); fallbacks: poetry install / pdm install
python -m talk_to_your_data.main  # run the bot
jupyter lab                  # start notebook server

ruff check .                 # lint
ruff format .                # format
```

No test suite is configured yet (no pytest or equivalent in dependencies).

## Architecture

The agent is a LangGraph pipeline with three nodes (see `system_design_mvp.png`):

1. **Intake** — parses the raw Slack message; applies guardrails that block personal-data queries before any SQL is generated
2. **Engine** — intent understanding → SQL generation via PandasAI → query execution → answer synthesis; talks to the database through the **semantic layer** (business-friendly schema abstraction over raw PostgreSQL)
3. **Output** — formats the synthesised result and posts it back to Slack

The semantic layer sits between Engine and PostgreSQL and must integrate cleanly with PandasAI so generated SQL is valid against it.

Phase 2 (not yet started) will add a **memory component** for multi-turn context.

## Tech Stack

- **PandasAI >= 3** — NLP-to-SQL translation and query execution
- **LangGraph >= 0.2** — reserved for Phase 2 (multi-turn memory); Phase 1 uses plain Python function calls
- **langchain-anthropic** — default LLM provider; swap for `langchain-openai` by changing the import and model config
- **Slack Bolt** — inbound/outbound Slack I/O
- **SQLAlchemy + psycopg2** — PostgreSQL connectivity

## Conventions

- Python **3.11 strictly** (`>=3.11,<3.12`) — do not use 3.12+ syntax
- Virtual environment in `.venv/` (gitignored)
- Secrets and connection strings in `.env` (gitignored) — load with `python-dotenv`; see `.env.example` for required keys
- Entry point: `talk_to_your_data/main.py`
- Ruff line length: 88; rules: E, F, I (pyflakes + isort)

## Working Style

- **Plan mode**: build iteratively, module by module — never plan the whole app at once; complete and validate one piece before moving to the next
- **Code style**: prefer 5 explicit, readable lines over a clever one-liner; don't write code unless it is necessary for the current task
- **Verbosity**: keep responses concise; elaborate only when the complexity genuinely warrants it
- **Diagnostic questions**: when the user asks "is this normal?" or "is this okay?", just answer the question — do not automatically propose a code fix unless they ask for one
