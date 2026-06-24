import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from talk_to_your_data import intake

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("message")
def handle_message(event, say):
    """Receive any user message, run intake, and route to the engine (stubbed)."""
    if event.get("bot_id"):
        return

    message = intake.process(event)
    reply_ts = message.thread_ts or event.get("ts")

    if message.blocked:
        say(text=f"Sorry, I can't answer that. {message.block_reason}", thread_ts=reply_ts)
        return

    # TODO: pass message to the Engine node
    say(text=f"Got your question: _{message.text}_\n(Engine not wired yet)", thread_ts=reply_ts)


def start():
    """Start the bot in Socket Mode."""
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
