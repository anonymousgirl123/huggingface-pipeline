from __future__ import annotations

from dotenv import load_dotenv
from app.rag.retriever import LocalRetriever
from app.clients.hf_local import HFLocalClient
from app.core.bot import ResilienceBot


def main() -> None:
    load_dotenv()

    question = "My API has intermittent 504 timeouts. Give a troubleshooting checklist."

    # ── Step 1: Test retrieval independently ──────────────────────
    print("\n===== RETRIEVAL TEST =====")
    retriever = LocalRetriever()
    results = retriever.retrieve(question)

    print(f"Query: {question}")
    print(f"Top-{len(results)} chunks retrieved:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] Source: {r['source']}")
        print(f"      Score:  {r['score']:.4f}")
        print(f"      Text:   {r['text'][:120]}...")
        print()

    # ── Step 2: Test full RAG bot response ────────────────────────
    print("===== RAG BOT RESPONSE =====")
    client = HFLocalClient()
    bot = ResilienceBot(client, retriever=retriever)
    response = bot.ask(question)

    print(response.text)


if __name__ == "__main__":
    main()
