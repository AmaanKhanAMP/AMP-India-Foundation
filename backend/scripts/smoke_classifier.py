"""Smoke test for pre-retrieval query classification."""

from app import create_app
from services.chat_service import process_message
from services.query_classifier import classify_query


CASES = [
    ("Hi", "greeting"),
    ("Assalamualaikum", "greeting"),
    ("thanks", "small_talk"),
    ("how are you", "small_talk"),
    ("who are you", "small_talk"),
    ("what can you do", "small_talk"),
    ("What scholarships do you have?", "amp_knowledge"),
    ("How can I donate?", "amp_knowledge"),
    ("Upcoming events", "amp_knowledge"),
    ("Tell me about Medical Projects", "amp_knowledge"),
    ("What color is the sky?", "general_knowledge"),
    ("Who invented the internet?", "general_knowledge"),
    ("How many planets are there?", "general_knowledge"),
    ("What is AI?", "general_knowledge"),
    ("Tell me a joke.", "general_knowledge"),
    ("What is Python?", "general_knowledge"),
    ("Can you help me hack Wi-Fi?", "out_of_scope"),
    ("xyzzy unknown thing", "out_of_scope"),
]


def main():
    app = create_app()
    with app.app_context():
        print("=== Classification ===")
        for text, expected in CASES:
            result = classify_query(text)
            ok = "OK" if result.category.value == expected else "FAIL"
            print(f"{ok:4} expected={expected:18} got={result.category.value:18} | {text}")

        print("\n=== End-to-end replies (no AMP leakage) ===")
        for text in [
            "What color is the sky?",
            "Who invented the internet?",
            "Can you help me hack Wi-Fi?",
            "What scholarships do you have?",
            "Hi",
        ]:
            r = process_message(text, session_id="clf-smoke")
            preview = r["response"][:140].replace("\n", " ")
            print(f"[{r['meta'].get('category')}] {text}")
            print(f"  -> {preview}\n")


if __name__ == "__main__":
    main()
