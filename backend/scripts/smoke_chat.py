"""Quick smoke test for Phase 2 chat conversational behavior."""

from app import create_app
from services.chat_service import process_message


def main():
    app = create_app()
    tests = [
        "Hi",
        "Hii",
        "Assalamualaikum",
        "hello",
        "thanks",
        "ok",
        "bye",
        "who are you",
        "what can you do",
        "help",
        "How can I donate to AMP India Foundation?",
        "Tell me about Scholarship Programs",
        "What upcoming events do you have?",
        "xyzzy unknown thing",
    ]
    with app.app_context():
        session = "smoke-conversation-1"
        for q in tests:
            r = process_message(q, session_id=session)
            preview = r["response"][:160].replace("\n", " | ")
            has_more = "more details" in r["response"].lower()
            print(f"{r['intent']:14} {r['confidence']:.2f} | more_details={has_more}")
            print(f"  Q: {q}")
            print(f"  A: {preview}")
            print()


if __name__ == "__main__":
    main()
