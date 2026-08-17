from typing import Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class ErrorState(TypedDict, total=False):
    raw_text: str

    category: Literal["command_error", "detailed_analysis", "ignore"]
    confidence: float

    error: Optional[str]
    description: Optional[str]
    logs: Optional[str]
    tech_stack: Optional[str]

    risk: Optional[Literal["High", "Medium", "Low"]]
    explanation: Optional[str]
    prevention: Optional[str]

    quick_fix: Optional[str]
    quick_explanation: Optional[str]


class Risk(BaseModel):
    risk: Literal["High", "Medium", "Low"] = Field(
        description="Overall risk level of the incident"
    )


class ErrorExtractor(BaseModel):
    error: str = Field(description="The core error message extracted from the message")

    logs: str = Field(description="The relevant log line from the extracted error")

    description: str = Field(
        description="Any user-provided context or description, empty string if none"
    )

    tech_stack: str = Field(
        description="Tech stack mentioned, empty string if not mentioned"
    )


class Explanation(BaseModel):
    explanation: str = Field(description="Clear explanation of why this error happened")


class Prevention(BaseModel):
    prevention: str = Field(
        description="Specific practical steps to prevent this error in the future"
    )


class QuickFix(BaseModel):
    quick_fix: str = Field(description="The corrected command that the user should run")

    explanation: str = Field(
        description="A very short explanation of what was wrong with the original command"
    )
