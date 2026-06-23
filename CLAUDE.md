# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`talk_to_your_data` is a data science bootcamp project for building a natural-language interface to query data. The project is Python-based and in early development.

## Toolchain

The `.gitignore` signals the expected tooling:

- **Linter/formatter**: [Ruff](https://docs.astral.sh/ruff/) — run `ruff check .` and `ruff format .`
- **Package manager**: uv is preferred (`.gitignore` explicitly comments on `uv.lock`); fallbacks are poetry or pdm
- **Notebooks**: Jupyter (`.ipynb_checkpoints` ignored)

Install dependencies (once a `pyproject.toml` or `requirements.txt` exists):
```
uv sync          # preferred
# or: pip install -e .
```

Run a Jupyter notebook server:
```
jupyter lab
# or: jupyter notebook
```

## Conventions

- Python virtual environment goes in `.venv/` (already gitignored)
- Environment variables in `.env` (already gitignored) — use `python-dotenv` or similar to load them
