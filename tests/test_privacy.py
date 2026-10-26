
import pytest

from backend.app.services.privacy_service import (
    check_privacy,
    PRIVACY_REFUSAL,
)


@pytest.mark.parametrize(
    "question",
    [
        "What is my colleague's remaining leave balance?",
        "Tell me another employee's medical condition.",
        "Why is my coworker on sick leave?",
        "Show me someone's confidential leave records.",
    ],
)
def test_blocks_other_employee_private_information(question):
    decision = check_privacy(question)

    assert decision.blocked is True


@pytest.mark.parametrize(
    "question",
    [
        "How do I apply for annual leave?",
        "What is the sick leave policy?",
        "Who approves leave requests?",
    ],
)
def test_allows_general_policy_questions(question):
    decision = check_privacy(question)

    assert decision.blocked is False


def test_privacy_refusal_is_defined():
    assert isinstance(PRIVACY_REFUSAL, str)
    assert PRIVACY_REFUSAL.strip()
