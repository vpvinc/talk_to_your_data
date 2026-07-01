import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from talk_to_your_data import engine, intake


class _HealthHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that returns 200 OK on any GET request.

    Render's free web service tier requires a process bound to PORT and spins
    down after 15 minutes of inactivity. This server runs on the main thread
    so Render sees an open port immediately. The Slack Socket Mode handler
    runs in a background thread. UptimeRobot pings this endpoint every 14
    minutes to prevent spin-down.
    """

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass  # suppress access logs


def _start_health_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), _HealthHandler).serve_forever()

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


def _start_slack_handler():
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
    print("[slack_bot] started in Socket Mode")


def start():
    """Start the bot: health server on main thread (satisfies Render), Slack in background."""
    threading.Thread(target=_start_slack_handler, daemon=True).start()
    _start_health_server()  # blocks forever on main thread — keeps the process alive
