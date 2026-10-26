
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PolicyResponse(BaseModel):
    """Metadata describing an indexed HR policy."""

    model_config = ConfigDict(from_attributes=True)

    policy_id: str
    title: str
    version: str
    effective_date: date | None = None
    section_count: int = Field(default=0, ge=0)


class PolicySectionResponse(BaseModel):
    """A section extracted from an HR policy."""

    section_number: str = ""
    heading: str
    content: str


class PolicySectionsResponse(BaseModel):
    """Policy metadata and its sections."""

    policy_id: str
    title: str
    version: str
    effective_date: date | None = None
    sections: list[PolicySectionResponse] = Field(default_factory=list)
