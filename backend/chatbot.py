"""Terminal chat about one prescription photo: python -m backend.chatbot path/to/photo.jpg
Memory is this process only. It is gone when you type exit."""
import sys
from pathlib import Path

from . import chat_reply, extract_prescription
from .safety import DISCLAIMER

if __name__ == "__main__":
    photo = Path(sys.argv[1])
    rows = extract_prescription(photo.read_bytes(), photo.name)
    for r in rows:
        print(f"- {r['medicine']} | {r['dosage']} | {r['frequency']}")
    print(f"\n{DISCLAIMER}\nAsk about these medicines. Type 'exit' to quit.\n")
    history = []  # session-bound memory
    while (q := input("You: ").strip()).lower() not in ("", "exit", "quit", "q"):
        a = chat_reply(history, rows, q)
        history += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        print(f"\nBot: {a}\n")
