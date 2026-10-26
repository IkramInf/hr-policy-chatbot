
import re
import unicodedata


MAX_QUESTION_LENGTH = 2000

# Permit ordinary whitespace, but reject other control characters.
DISALLOWED_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def validate_question(question: str) -> str:
    """
    Normalize and validate an employee question.

    Raises ValueError if the input is invalid.
    """
    if not isinstance(question, str):
        raise ValueError("Question must be text.")

    cleaned = unicodedata.normalize("NFC", question).strip()

    if not cleaned:
        raise ValueError("Question cannot be empty.")

    if len(cleaned) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"Question cannot exceed {MAX_QUESTION_LENGTH} characters."
        )

    if DISALLOWED_CONTROL_CHARS.search(cleaned):
        raise ValueError("Question contains unsupported control characters.")

    return cleaned
