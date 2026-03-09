import sys

from dotenv import load_dotenv

from app.clients.hf_local import HFLocalClient
from app.core.bot import ResilienceBot


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print('Usage: python -m app.main "your question"')
        return

    question = sys.argv[1]

    client = HFLocalClient()
    bot = ResilienceBot(client)

    resp = bot.ask(question)

    print("\nResilienceBot:\n")
    print(resp.text)

    print(f"\nModel: {resp.model_name} | Latency: {resp.usage.get('latency_ms')} ms")


if __name__ == "__main__":
    main()
    