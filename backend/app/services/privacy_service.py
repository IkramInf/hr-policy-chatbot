
import re
from dataclasses import dataclass


PRIVACY_REFUSAL = (
    "I can't provide another employee's confidential leave or medical "
    "information. Please contact HR for authorized assistance."
)

# Terms that may indicate access to individual employee information.
SENSITIVE_TERMS = re.compile(
    r"\b("
    r"leave balance|leave history|leave record|"
    r"days of leave|days off taken|absence record|"
    r"medical details|medical condition|diagnosis|"
    r"reason for (?:leave|absence)|sick leave record|"
    r"health records|medical records"
    r")\b",
    re.IGNORECASE,
)

# Clues that the request concerns someone other than the questioner.
OTHER_PERSON_TERMS = re.compile(
    r"\b("
    r"another employee|other employee|my colleague|"
    r"my coworker|my co-worker|my manager|"
    r"my teammate|someone else's|somebody else's|"
    r"employee named|colleague named|"
    r"what about [A-Z][a-z]+|"
    r"tell me about [A-Z][a-z]+"
    r")\b",
    re.IGNORECASE,
)

# Common explicit requests for a named person's confidential details.
NAMED_PERSON_REQUEST = re.compile(
    r"\b("
    r"what is|what are|show me|tell me|"
    r"find|reveal|give me|how many"
    r")\b.*\b("
    r"leave balance|leave history|medical details|"
    r"medical condition|reason for absence|"
    r"health records|medical records"
    r")\b",
    re.IGNORECASE,
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

    has_sensitive_data = bool(SENSITIVE_TERMS.search(text))
    if not has_sensitive_data:
        return PrivacyDecision(blocked=False)

    # Explicit references to someone else's personal information.
    has_other_person_reference = bool(OTHER_PERSON_TERMS.search(text))

    # Catch some direct questions about a named individual.
    has_named_person_request = bool(NAMED_PERSON_REQUEST.search(text))

    if has_other_person_reference or has_named_person_request:
        return PrivacyDecision(
            blocked=True,
            reason="Request concerns another person's confidential data.",
        )

    return PrivacyDecision(blocked=False)
