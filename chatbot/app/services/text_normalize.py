"""Shared text normalization and common typo fixes for routing / retrieval."""

from __future__ import annotations

import re

# Common user misspellings → canonical forms (order matters for multi-word first)
SPELL_FIXES = (
    ("jop fair", "job fair"),
    ("jopfare", "job fair"),
    ("jobfare", "job fair"),
    ("jobb fair", "job fair"),
    ("job fiar", "job fair"),
    ("job faire", "job fair"),
    ("volnteer", "volunteer"),
    ("volunter", "volunteer"),
    ("voluntear", "volunteer"),
    ("volanteer", "volunteer"),
    ("volenteer", "volunteer"),
    ("vollunteer", "volunteer"),
    ("volunteeer", "volunteer"),
    ("scholorship", "scholarship"),
    ("scholership", "scholarship"),
    ("scholarhsip", "scholarship"),
    ("scolarship", "scholarship"),
    ("scholarshp", "scholarship"),
    ("scholarsip", "scholarship"),
    ("scholaship", "scholarship"),
    ("skolarship", "scholarship"),
    ("scholer", "scholarship"),
    ("employement", "employment"),
    ("emplyment", "employment"),
    ("empolyment", "employment"),
    ("employmnt", "employment"),
    ("emploment", "employment"),
    ("employ ment", "employment"),
    ("helthcare", "healthcare"),
    ("contat", "contact"),
    ("contcat", "contact"),
    ("tu kon", "tu kaun"),
    ("tum kon", "tum kaun"),
    ("aap kon", "aap kaun"),
    ("kon hai", "kaun hai"),
    ("aidf", "aif"),
    ("asslam", "assalamualaikum"),
    ("asalam", "assalamualaikum"),
    ("evennts", "events"),
    ("eveents", "events"),
    ("evnts", "events"),
    ("evenet", "event"),
    ("evnet", "event"),
    ("donaton", "donation"),
    ("donaion", "donation"),
    ("donetion", "donation"),
    ("donaiton", "donation"),
    ("donatiion", "donation"),
    ("donat", "donate"),
    ("donte", "donate"),
    ("donatione", "donation"),
    ("contat", "contact"),
    ("contcat", "contact"),
    ("helthcare", "healthcare"),
    ("emploment", "employment"),
    ("aidf", "aif"),
    ("asslam", "assalamualaikum"),
    ("asalam", "assalamualaikum"),
    ("adres", "address"),
    ("adress", "address"),
    ("adresss", "address"),
    ("addres", "address"),
    ("upcomming", "upcoming"),
    ("upoming", "upcoming"),
    ("locaton", "location"),
    ("loction", "location"),
    ("ofis", "office"),
    ("offic", "office"),
    ("naukari", "naukri"),
    ("emil", "email"),
    ("emial", "email"),
    ("telephon", "telephone"),
    ("phne", "phone"),
    ("timimg", "timing"),
    ("gareb", "gareeb"),
    ("assalamualaikum", "assalamualaikum"),
    ("asalamualaikum", "assalamualaikum"),
    ("asalamualakium", "assalamualaikum"),
    ("asalamualikum", "assalamualaikum"),
    ("assalamualikum", "assalamualaikum"),
    ("salamu alaikum", "assalamualaikum"),
    ("jazakallah", "jazakallah"),
    ("jazakalla", "jazakallah"),
    ("mashaallah", "mashallah"),
    ("ma sha allah", "mashallah"),
    ("inshalla", "inshallah"),
    ("in sha allah", "inshallah"),
    ("allahafiz", "allah hafiz"),
    ("khudahafiz", "khuda hafiz"),
)


def apply_spell_fixes(text: str) -> str:
    """Replace common misspellings as whole words/phrases (never partial stems)."""
    out = text or ""
    for bad, good in SPELL_FIXES:
        # Word-boundary safe: "offic" must not rewrite "office" → "officee"
        pattern = rf"(?<![a-zA-Z]){re.escape(bad)}(?![a-zA-Z])"
        out = re.sub(pattern, good, out, flags=re.I)
    return out


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def normalize_for_match(text: str) -> str:
    """Lowercase, strip trailing punctuation, apply spell fixes — for intent matching."""
    text = normalize_whitespace(text).lower()
    text = re.sub(r"[!?.،,]+$", "", text)
    text = apply_spell_fixes(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
