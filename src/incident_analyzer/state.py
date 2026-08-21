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
    has_fix: Optional[bool]

    # V3 - Agent Action
    can_fix: Optional[bool]
    fix_reason: Optional[str]
    action_response: Optional[str]
    tool_used: Optional[str]


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
    title: str = Field(
        description=(
            "A short, specific label for the error, e.g. "
            "'Git subcommand not recognized' or "
            "'PowerShell command not found'. "
            "Never output 'Unknown error' or any vague/generic placeholder."
        )
    )

    has_fix: bool = Field(
        description=(
            "True if a corrected command can be confidently determined, "
            "False if the intended command cannot be reliably guessed."
        )
    )

    quick_fix: str = Field(
        description=(
            "The corrected command the user should run. "
            "If has_fix is False, set this to an empty string."
        )
    )

    explanation: str = Field(
        description=(
            "A very short explanation of what was wrong with the original command"
        )
    )


class ActionDecision(BaseModel):
    can_fix: bool = Field(
        description=(
            "True if the error can be safely corrected by "
            "modifying the source code. False otherwise"
        )
    )
    fix_reason: str = Field(
        description=(
            "Short explanation of why the error can or cannot "
            "be automatically corrected"
        )
    )

class SuggestedFix(BaseModel):
    can_fix: bool = Field(
        description="True if a confident, safe fix can be determined from the given file content."
    )
    old_code: str = Field(
        description="The exact existing code block to replace. Must match the given file content exactly, including whitespace. Empty string if can_fix is False."
    )
    new_code: str = Field(
        description="The corrected replacement code. Empty string if can_fix is False."
    )
    explanation: str = Field(
        description="A short explanation of the fix, or why it could not be determined."
    )
