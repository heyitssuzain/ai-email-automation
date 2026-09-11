import pytest
from pydantic import ValidationError

from app.ai.schemas import EmailAnalysis


def test_valid_email_analysis():
    result = EmailAnalysis(
        category="Customer Support",
        priority="HIGH",
        intent="Customer wants help with their order.",
        summary="Customer is asking for assistance with an order.",
        requires_reply=True,
    )

    assert result.category == "Customer Support"
    assert result.priority == "HIGH"
    assert result.requires_reply is True


def test_invalid_category():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="Invalid Category",
            priority="HIGH",
            intent="Customer needs help.",
            summary="Customer needs assistance.",
            requires_reply=True,
        )


def test_invalid_priority():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="Customer Support",
            priority="CRITICAL",
            intent="Customer needs help.",
            summary="Customer needs assistance.",
            requires_reply=True,
        )


def test_missing_required_field():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="Customer Support",
            priority="HIGH",
            intent="Customer needs help.",
            requires_reply=True,
        )


def test_empty_intent_rejected():
    with pytest.raises(ValidationError):
        EmailAnalysis(
            category="Customer Support",
            priority="HIGH",
            intent="",
            summary="Customer needs assistance.",
            requires_reply=True,
        )