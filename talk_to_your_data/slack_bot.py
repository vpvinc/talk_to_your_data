import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from talk_to_your_data import engine, intake

app = App(token=os.environ["SLACK_BOT_TOKEN"], process_before_response=True)

_seen_msg_ids: set[str] = set()


@app.event("message")
def handle_message(event, say):
    """Receive any user message, run intake, and route to the engine."""
    if event.get("bot_id"):
        return

    msg_id = event.get("client_msg_id")
    if msg_id in _seen_msg_ids:
        return
    if msg_id:
        _seen_msg_ids.add(msg_id)

    print(f"[slack_bot] received: {event}")

    message = intake.process(event)
    reply_ts = message.thread_ts or event.get("ts")

    if message.blocked:
        say(text=f"Sorry, I can't answer that. {message.block_reason}", thread_ts=reply_ts)
        return

    try:
        answer = engine.process(message)
    except Exception as exc:
        print(f"[slack_bot] engine error: {exc}")
        say(text="Sorry, something went wrong while processing your question.", thread_ts=reply_ts)
        return

    say(text=answer, thread_ts=reply_ts)


def start():
    """Start the bot in Socket Mode."""
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
    print("[slack_bot] started in Socket Mode")
