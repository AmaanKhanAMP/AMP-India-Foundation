"""Strip internal prompt/reasoning leakage from model outputs before returning to clients."""

from __future__ import annotations

import re
from typing import Optional

from app.services.language_service import Language
from app.services.prompt_service import CLARIFY_RESPONSE, t
from app.services.security_service import scrub_secrets
from app.services.response_composer import clean_response

# Markers that indicate the model echoed internal instructions / debug
_LEAK_BLOCK_START = re.compile(
    r"(?im)^(?:\s*)(?:"
    r"/?\s*rules?\s*check|"
    r"hard rules?|"
    r"system prompt|"
    r"internal instructions?|"
    r"hidden (?:instructions?|prompt)|"
    r"thought process|"
    r"chain[- ]of[- ]thought|"
    r"debug output|"
    r"prompt template|"
    r"retrieved knowledge\s*\(verified|"
    r"instructions\s*:|"
    r"user language\s*:|"
    r"verified knowledge\s*:|"
    r"\[source:\s*"
    r").*$"
)

_LEAK_INLINE = re.compile(
    r"(?i)(?:"
    r"/?\s*rules?\s*check\s*:?|"
    r"\brule\s*\d+\s*:|"
    r"hard rules?\s*:|"
    r"system prompt|"
    r"internal instructions?|"
    r"never reveal system|"
    r"answer only using the retrieved knowledge|"
    r"answer ONLY using|"
    r"do not dump unrelated contact|"
    r"never invent, guess, or fabricate|"
    r"chain[- ]of[- ]thought|"
    r"prompt template|"
    r"hidden metadata"
    r")"
)

_LINE_RULE_ECHO = re.compile(
    r"(?im)^\s*(?:\d+[\).\]]\s+|[-*•]\s*)?(?:"
    r"answer only using|"
    r"never invent|"
    r"never answer topics outside|"
    r"if the retrieved knowledge|"
    r"reply in the user.?s language|"
    r"use conversation history|"
    r"maintain a professional|"
    r"write natural full sentences|"
    r"never reveal system|"
    r"never follow user instructions|"
    r"do not dump unrelated|"
    r"if asked what model"
    r").*$"
)


def _strip_leak_blocks(text: str) -> str:
    lines = (text or "").splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        if _LEAK_BLOCK_START.search(line) or _LINE_RULE_ECHO.search(line):
            skipping = True
            continue
        # Stop skipping when we hit a blank line after a rules block, or a normal sentence
        if skipping:
            if not line.strip():
                skipping = False
            continue
        if _LEAK_INLINE.search(line) and len(line.strip()) < 220:
            continue
        kept.append(line)
    cleaned = "\n".join(kept).strip()
    # Remove residual inline leak phrases
    cleaned = _LEAK_INLINE.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip(" \n:-")


def looks_like_prompt_leak(text: str) -> bool:
    lower = (text or "").lower()
    markers = (
        "rules check",
        "hard rules",
        "system prompt",
        "rule 1:",
        "rule 2:",
        "answer only using the retrieved",
        "internal instructions",
        "prompt template",
        "thought process",
        "chain-of-thought",
        "chain of thought",
    )
    return any(m in lower for m in markers)


def format_user_response(
    text: str,
    *,
    language: Language | str = Language.ENGLISH,
    fallback: Optional[str] = None,
) -> str:
    """
    Final gate before the API returns text to the frontend.
    Ensures only a conversational answer is shown — never prompts, rules, or debug.
    """
    cleaned = scrub_secrets((text or "").strip())
    if not cleaned:
        return fallback if fallback is not None else t(CLARIFY_RESPONSE, language)

    if looks_like_prompt_leak(cleaned):
        cleaned = _strip_leak_blocks(cleaned)

    # Second pass if still leaking
    if looks_like_prompt_leak(cleaned):
        cleaned = _strip_leak_blocks(cleaned)

    # Strip raw FAQ / chunk dump patterns and document titles
    cleaned = re.sub(r"(?im)^Q:\s*.+$", "", cleaned)
    cleaned = re.sub(r"(?im)^A:\s*", "", cleaned)
    cleaned = re.sub(r"(?im)^#{1,6}\s+.+$", "", cleaned)
    cleaned = re.sub(r"(?im)^\[source:\s*.+$", "", cleaned)
    cleaned = re.sub(
        r"(?im)^\s*(?:\*\*)?(?:Projects?\s*&\s*Programs?|About(?:\s+Us)?|Contact(?:\s+Us)?|"
        r"Donations?|Volunteering|Scholarships?|Events?|Employment)"
        r"(?:\s*[—\-:]\s*AMP India Foundation)?(?:\*\*)?\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(r"(?im)^\s*[—\-]\s*AMP India Foundation\s*$", "", cleaned)
    cleaned = re.sub(r"\*\*|__", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    cleaned = clean_response(cleaned, max_words=160)

    if not cleaned or looks_like_prompt_leak(cleaned) or len(cleaned) < 8:
        return fallback if fallback is not None else t(CLARIFY_RESPONSE, language)

    # Secret / infra leakage after strip
    toxic = (
        "gemini_api_key",
        "pinecone_api_key",
        "traceback",
        ".env",
        "developer mode",
        "ignore previous instructions",
    )
    lower = cleaned.lower()
    if any(x in lower for x in toxic):
        return fallback if fallback is not None else t(CLARIFY_RESPONSE, language)

    return cleaned.strip()
