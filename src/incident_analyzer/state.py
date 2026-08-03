from typing import Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class ErrorState(TypedDict):
    raw_text: str
    error: Optional[str]
    description: Optional[str]
    risk: Optional[Literal["High", "Medium", "Low"]]
    logs: Optional[str]
    tech_stack: Optional[str]
    explanation: Optional[str]
    prevention: Optional[str]


class Risk(BaseModel):
    risk: Literal["High", "Medium", "Low"] = Field(
        description="Overall risk level of the incident"
    )


class ErrorExtractor(BaseModel):
    error: str = Field(description="The core error message extracted from the message")
    logs: str = Field(description="The relevant log line from the extracted code")
    description: str = Field(
        description="Any user-provided context or description, empty string if none"
    )
    tech_stack: str = Field(
        description="Tech stack mentioned, empty string if not mentioned"
    )


class Suggestion(BaseModel):
    explanation: str = Field(
        description=(
            "Clear explanation of why this error happened and why it has this risk level"
        )
    )
    prevention: str = Field(
        description="How to prevent this type of incident from happening again"
    )
