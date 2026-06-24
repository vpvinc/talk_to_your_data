from dotenv import load_dotenv

load_dotenv()

from talk_to_your_data import engine  # noqa: E402
from talk_to_your_data.intake import IntakeMessage  # noqa: E402

if __name__ == "__main__":
    print("Engine ready. Type your question (Ctrl+C to quit).\n")
    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not question:
            continue
        msg = IntakeMessage(
            text=question,
            user_id="cli",
            channel_id="cli",
            thread_ts=None,
            blocked=False,
            block_reason=None,
        )
        print(f"Bot: {engine.process(msg)}\n")
