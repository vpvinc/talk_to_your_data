import re
from dataclasses import dataclass

# Terms that indicate a query for personal/sensitive data
_BLOCKED_TERMS = [
    "password",
    "ssn",
    "social security",
    "credit card",
    "phone number",
    "date of birth",
    "home address",
    "personal email",
    "private",
]


@dataclass
class IntakeMessage:
    """Parsed and validated representation of an inbound Slack message."""

    text: str
    user_id: str
    channel_id: str
    thread_ts: str | None
    blocked: bool
    block_reason: str | None


def _strip_bot_mention(text: str) -> str:
    """Remove the leading @bot mention that Slack prepends to app_mention events."""
    return re.sub(r"<@[A-Z0-9]+>", "", text).strip()


def _check_guardrails(text: str) -> tuple[bool, str | None]:
    """Return (True, reason) if the query touches restricted personal-data terms, else (False, None)."""
    lower = text.lower()
    for term in _BLOCKED_TERMS:
        if term in lower:
            return True, f"Queries involving '{term}' are not allowed."
    return False, None


def process(event: dict) -> IntakeMessage:
    """Parse a raw Slack event dict into an IntakeMessage, applying guardrails."""
    raw_text = event.get("text", "")
    text = _strip_bot_mention(raw_text)
    user_id = event.get("user", "")
    channel_id = event.get("channel", "")
    thread_ts = event.get("thread_ts")

    blocked, block_reason = _check_guardrails(text)

    return IntakeMessage(
        text=text,
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        blocked=blocked,
        block_reason=block_reason,
    )
