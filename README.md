# talk_to_your_data

A Slack bot that lets non-technical users query a PostgreSQL database in plain language — no SQL required.

> "Who are the top 5 customers by revenue last quarter?"  
> "What is the average session duration by activity type?"  
> "Show me DAU for the past 30 days."

Answers are returned directly in Slack as readable text or formatted tables.

## How it works

```
Slack message → Intake (guardrails) → Engine (PandasAI NLP-to-SQL) → Slack reply
```

| Component | Role |
|---|---|
| **Intake** | Parses the Slack message; blocks queries that touch personal data (PII guardrails) |
| **Engine** | Translates the question to SQL via PandasAI, executes it against PostgreSQL, and synthesises a readable answer |
| **Semantic layer** | Business-friendly schema abstraction over the raw database — steers the LLM toward the right tables and columns |
| **Slack bot** | Receives inbound messages via Socket Mode, deduplicates retries, posts answers in the thread |

Phase 1 is a linear pipeline with plain Python function calls. Phase 2 (not yet started) will introduce LangGraph for multi-turn conversational memory.

## Database

The bot connects to a PostgreSQL database with the following tables:

**`public` schema — raw operational tables**

| Table | Description |
|---|---|
| `users` | Registered users: signup date, country, device type |
| `sessions` | One row per user session: duration, activity type |
| `subscriptions` | Subscription lifecycle: plan, status, start/end dates |
| `payments` | Payment transactions: amount, method, date |

**`marts` schema — pre-aggregated business metrics**

| Table | Description |
|---|---|
| `user_activity_metrics` | Daily DAU / WAU / MAU — use for engagement trend questions |
| `user_revenue_summary` | Per-user lifetime revenue — use for revenue aggregations |

## Setup

**1. Clone and install dependencies**

```bash
poetry install
# or: uv sync
```

**2. Configure environment variables**

Copy `.env.example` to `.env` and fill in the values:

```
DB_HOST=...
DB_PORT=5432
DB_USER=...
DB_PASS=...
DB_NAME=...

OPENAI_API_KEY=...

SLACK_BOT_TOKEN=...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=...
```

The LLM defaults to `gpt-4.1-mini` via LiteLLM. Change the model in `engine.py` if needed.

**3. Run the bot**

```bash
python -m talk_to_your_data.main
```

## Project structure

```
talk_to_your_data/
├── main.py            # Entry point — starts the Slack bot
├── slack_bot.py       # Slack Bolt event handler (Socket Mode)
├── intake.py          # Message parsing and PII guardrails
├── engine.py          # PandasAI agent — NLP-to-SQL and answer synthesis
└── semantic_layer.py  # Schema definitions for all 6 tables
datasets/              # PandasAI dataset cache (auto-generated at startup)
scripts/               # SQL utilities (e.g. metadata queries)
```

## Development

```bash
ruff check .    # lint
ruff format .   # format
```

Python 3.11 strictly (`>=3.11,<3.12`).

## Guardrails

Queries containing the following terms are blocked before any SQL is generated:
`password`, `ssn`, `social security`, `credit card`, `phone number`, `date of birth`, `home address`, `personal email`, `private`.

## Deployment (Render)

The bot is hosted on Render as a free Web Service. Because it uses Slack's Socket Mode (an outbound WebSocket connection — no inbound HTTP needed), a small health endpoint runs alongside it so Render has a port to scan.

**How the two tasks coexist**

When you run `python -m talk_to_your_data.main`, Python starts one worker — the *main thread* — that executes code line by line. A single worker can only do one thing at a time, so we hire a second one with `threading.Thread(...)`. Now two things happen simultaneously.

- **Main thread → health server.** Binds to the port Render expects, answers every request with `200 OK`. Render sees an open port immediately and keeps the service alive.
- **Background thread → Slack connection.** Opens a persistent connection to Slack's servers and waits for messages. Think of it like picking up a phone and keeping the line open — Slack talks to you through that line whenever someone writes to the bot.

The background thread is marked `daemon=True`, which means it automatically stops if the main thread ever exits (like a team that goes home when the manager does). This prevents the process from hanging if the Slack connection crashes — the health server stays up, and Render doesn't kill the service.

To prevent Render's free tier from spinning the service down after 15 minutes of inactivity, set up a free monitor on [UptimeRobot](https://uptimerobot.com) pointing at your Render URL with a 14-minute interval.

## Limitations (Phase 1)

- No conversational memory — each message is answered independently
- No chart or visualisation output
- Read-only — no write operations on the database
- No per-user access control beyond the PII guardrails
