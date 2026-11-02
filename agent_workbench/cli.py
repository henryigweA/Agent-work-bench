import logging
from .config import Settings
from .gemini import GeminiAgent

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    try:
        agent = GeminiAgent(Settings.from_env())
    except RuntimeError as exc:
        print(f"Setup error: {exc}")
        return

    print("\nAgent Workbench")
    print("Try calculations, weather lookups, UTC time or public GitHub repository checks.")
    print("Type 'exit' or 'quit' to close.\n")
    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not prompt:
            continue
        try:
            print(f"\nAgent: {agent.ask(prompt)}\n")
        except (RuntimeError, ValueError) as exc:
            print(f"Error: {exc}\n")

if __name__ == "__main__":
    main()
