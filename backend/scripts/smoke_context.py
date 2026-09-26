"""Smoke test for session context + module FAQ follow-ups."""

from app import create_app
from services.chat_service import process_message
from services.session_context import clear_context


def ask(session, text):
    r = process_message(text, session_id=session)
    preview = r["response"][:160].replace("\n", " | ")
    ctx = (r.get("meta") or {}).get("context") or {}
    print(f"Q: {text}")
    print(f"  intent={r['intent']} topic={ctx.get('last_topic')} entity={ctx.get('last_entity')}")
    print(f"  A: {preview}")
    print()
    return r


def main():
    app = create_app()
    with app.app_context():
        session = "ctx-smoke-1"
        clear_context(session)

        print("=== Volunteer follow-ups ===")
        ask(session, "How do I register for volunteering?")
        ask(session, "Do I have to pay?")
        ask(session, "Can students volunteer?")

        print("=== Scholarship follow-ups ===")
        clear_context(session)
        ask(session, "Tell me about scholarships.")
        ask(session, "Who can apply?")
        ask(session, "Is there any fee?")
        ask(session, "When is the deadline?")

        print("=== Job fair follow-ups ===")
        clear_context(session)
        ask(session, "Tell me about the National Mega Job Fair")
        ask(session, "Do I have to pay?")
        ask(session, "Is placement guaranteed?")

        print("=== Identity / leadership ===")
        clear_context(session)
        ask(session, "Who are you?")
        ask(session, "Who is the head of AIF?")
        ask(session, "Who founded AMP?")

        print("=== No long repeat on follow-up ===")
        clear_context(session)
        r1 = ask(session, "What upcoming events do you have?")
        r2 = ask(session, "Do I have to pay?")
        assert "Employability Training" not in r2["response"]
        assert "free" in r2["response"].lower()
        print("OK: follow-up did not dump full events list")


if __name__ == "__main__":
    main()
