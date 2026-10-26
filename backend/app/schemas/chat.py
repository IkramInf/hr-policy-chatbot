
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Validated request body for POST /api/chat."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The employee's question about the HR policy.",
        examples=["How do I apply for annual leave?"],
    )


class PolicySourceResponse(BaseModel):
    """A policy section returned as a citation."""

    policy_id: str | None = None
    policy_title: str
    policy_version: str
    section_number: str = ""
    section_heading: str


class ChatResponse(BaseModel):
    """Validated response returned by POST /api/chat."""

    answer: str
    sources: list[PolicySourceResponse] = Field(default_factory=list)
    blocked: bool = False
