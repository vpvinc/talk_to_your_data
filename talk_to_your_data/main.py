from dotenv import load_dotenv

load_dotenv()

from talk_to_your_data.slack_bot import start  # noqa: E402

if __name__ == "__main__":
    start()
