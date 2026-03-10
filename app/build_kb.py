from __future__ import annotations

from dotenv import load_dotenv
from app.rag.build_index import build_and_save_index


def main() -> None:
    load_dotenv()
    build_and_save_index()
    print("\nKB build complete. Files written to data/index\n")


if __name__ == "__main__":
    main()
