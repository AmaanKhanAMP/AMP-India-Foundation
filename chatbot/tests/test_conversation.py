"""Unit tests for conversational intents (greeting / small talk / thanks / goodbye)."""

import unittest

from app.services.ai_service import ai_service
from app.services.conversation_service import classify_conversation, reply_for
from app.services.intent_router import Intent, route_intent
from app.services.language_service import Language


class ConversationRoutingTests(unittest.IsolatedAsyncioTestCase):
    def test_greetings_route(self):
        cases = [
            "Hi",
            "Hello",
            "Hey",
            "Hii",
            "Hello ji",
            "Hi bro",
            "Yo",
            "What's up",
            "Namaste",
            "नमस्ते",
            "हैलो",
            "Salaam",
            "Salam",
            "Assalamualaikum",
            "Adaab",
            "Good Morning",
            "Good Afternoon",
            "Good Evening",
            "Kya haal hai",
        ]
        for msg in cases:
            route = route_intent(msg)
            self.assertIn(
                route.intent,
                {Intent.GREETING, Intent.SMALL_TALK},
                msg,
            )
            self.assertTrue(route.canned_response, msg)
            self.assertFalse(route.uses_rag, msg)

    def test_small_talk_route(self):
        cases = [
            "How are you",
            "How are you doing",
            "How's your day",
            "Kaise ho",
            "Kaise hai aap",
            "Kya haal hai",
            "Sab theek",
            "Aur batao",
            "Aur kya chal raha hai",
            "Kaisa chal raha hai",
        ]
        for msg in cases:
            route = route_intent(msg)
            self.assertIn(route.intent, {Intent.GREETING, Intent.SMALL_TALK}, msg)
            self.assertTrue(str(route.canned_response or "").startswith("__CONV__"), msg)

    def test_thanks_and_goodbye(self):
        for msg in ("Thanks", "Thank you", "Shukriya", "JazakAllah"):
            self.assertEqual(route_intent(msg).intent, Intent.SMALL_TALK, msg)
        for msg in (
            "Bye",
            "byee",
            "byeee",
            "ok bye",
            "thanks bye",
            "goodbye",
            "see you",
            "take care",
            "Allah Hafiz",
            "Khuda Hafiz",
            "fi amanillah",
            "Good Night",
        ):
            route = route_intent(msg)
            self.assertEqual(route.intent, Intent.GOODBYE, msg)
            self.assertFalse(route.uses_rag, msg)

    def test_casual_never_rag(self):
        cases = [
            "kya kar rahe ho",
            "kaise ho",
            "bore ho?",
            "tum kaun ho",
            "tujhse door mai ek hi wajah ke liye hu",
        ]
        for msg in cases:
            route = route_intent(msg)
            self.assertIn(route.intent, {Intent.SMALL_TALK, Intent.GREETING, Intent.ASSISTANT_IDENTITY, Intent.CASUAL_CHAT}, msg)
            self.assertFalse(route.uses_rag, msg)

    def test_empathy_help_never_rag(self):
        for msg in ("paise chahiye", "madad chahiye", "help chahiye"):
            route = route_intent(msg)
            self.assertEqual(route.intent, Intent.SMALL_TALK, msg)
            self.assertFalse(route.uses_rag, msg)
            self.assertIn("need_help", route.reason or route.canned_response or "", msg)

    def test_never_rag_for_conversation(self):
        for msg in ("hello", "kaise hai aap", "aur batao", "good night"):
            self.assertFalse(route_intent(msg).uses_rag, msg)

    def test_example_replies_content(self):
        hello = reply_for("hello", Language.ENGLISH)
        self.assertIn("Hello!", hello)
        self.assertIn("AMP India Foundation", hello)

        salam = reply_for("salam", Language.HINGLISH)
        self.assertIn("Wa Alaikum Assalam", salam)
        self.assertIn("swagat", salam)

        how = reply_for("how_are_you", Language.HINGLISH)
        self.assertIn("theek", how.lower())
        self.assertIn("AMP India Foundation", how)

        aur = reply_for("aur_batao", Language.HINGLISH)
        self.assertIn("badhiya", aur.lower())

        night = reply_for("good_night", Language.HINGLISH)
        self.assertIn("Good night", night)

        thanks = reply_for("thanks", Language.HINGLISH)
        self.assertIn("shukriya", thanks.lower())

    async def test_chat_never_unavailable_for_conversation(self):
        banned = "couldn't find verified information"
        messages = [
            "hello",
            "Hello",
            "kaise hai aap",
            "Aur batao",
            "Good Night",
            "Shukriya",
            "Salam",
            "नमस्ते",
            "Hi bro",
            "What's up",
        ]
        for msg in messages:
            res = await ai_service.chat(msg, session_id="conv-unit")
            self.assertNotIn(banned, res["response"].lower(), msg)
            self.assertIn(res["intent"], {"greeting", "small_talk", "goodbye", "assistant_identity", "casual_chat"}, msg)
            self.assertFalse(res["meta"].get("rag_used"), msg)
            self.assertFalse(res["meta"].get("gemini_used"), msg)

    def test_classify_helper(self):
        hit = classify_conversation("Kaise hai aap")
        self.assertIsNotNone(hit)
        self.assertEqual(hit[0], Intent.SMALL_TALK)


if __name__ == "__main__":
    unittest.main()
