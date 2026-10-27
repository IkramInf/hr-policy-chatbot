
import re
from dataclasses import dataclass


PRIVACY_REFUSAL = (
    "I can't provide another employee's confidential leave or medical "
    "information. Please contact HR for authorized assistance."
)

# Personal leave / medical details (any phrasing).
SENSITIVE_TERMS = re.compile(
    r"\b("
    r"leave (?:balance|history|records?|days|taken)|"
    r"days? (?:off|taken|of leave|left|remaining)|"
    r"(?:sick|medical|on|taken|took) leave|"
    r"sick|ill|illness|medical|diagnosis|health|absen\w*|"
    r"reason for|why .{0,40}\b(?:leave|off)|"
    r"how (?:many|much) .{0,40}\b(?:taken|used|left|remaining)"
    r")\b",
    re.IGNORECASE,
)

# Clues that the question concerns someone other than the asker.
OTHER_PERSON_TERMS = re.compile(
    r"\b(another|other|someone|somebody|colleagues?|co-?workers?|"
    r"teammates?|team members?|subordinates?|he|she|his|her|him|"
    r"employee named|someone else's)\b",
    re.IGNORECASE,
)

# Capitalised words that are NOT person names (leave types, company terms).
_NOT_NAMES = {
    "annual", "casual", "sick", "maternity", "paternity", "marriage",
    "bereavement", "compensatory", "off", "leave", "hr", "xyz", "company",
    "policy", "section", "peoplehub", "department", "head", "managing",
    "director", "probation", "friday", "saturday", "sunday", "monday",
    "tuesday", "wednesday", "thursday", "lwp", "i",
}


def _mentions_named_person(text: str) -> bool:
    """True if a capitalised word that looks like a name appears mid-sentence."""
    words = re.findall(r"[A-Za-z']+", text)
    return any(
        re.fullmatch(r"[A-Z][a-z]+(?:'s)?", word)
        and word.lower().removesuffix("'s") not in _NOT_NAMES
        for word in words[1:]
    )


@dataclass(frozen=True)
class PrivacyDecision:
    blocked: bool
    reason: str | None = None


def check_privacy(question: str) -> PrivacyDecision:
    """
    Block likely requests for another person's confidential information.

    This rule-based check is a basic safeguard, not a complete
    privacy classifier.
    """
    if not question or not question.strip():
        return PrivacyDecision(
            blocked=False,
            reason=None,
        )

    text = question.strip()

    if not SENSITIVE_TERMS.search(text):
        return PrivacyDecision(blocked=False)

    about_someone_else = bool(
        OTHER_PERSON_TERMS.search(text) or _mentions_named_person(text)
    )

    if about_someone_else:
        return PrivacyDecision(
            blocked=True,
            reason="Request concerns another person's confidential data.",
        )

    return PrivacyDecision(blocked=False)
