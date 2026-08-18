from .llm import structured_call
from .prompts import (
    build_error_explanation_prompt,
    build_error_prevention_prompt,
    build_extractor_prompt,
    build_risk_prompt,
    build_quick_fix_prompt,
)
from .state import (
    ErrorExtractor,
    ErrorState,
    Risk,
    Explanation,
    Prevention,
    QuickFix,
)
from .guardial import classify_error


def quick_fix_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_quick_fix_prompt(state),
        schema=QuickFix.model_json_schema(),
        schema_name="quick_fix",
    )

    return {
        "quick_fix": result["quick_fix"],
        "quick_explanation": result["explanation"],
        "error": result["title"],
        "logs": state["raw_text"],
        "has_fix": result["has_fix"],
    }


def extractor_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_extractor_prompt(state),
        schema=ErrorExtractor.model_json_schema(),
        schema_name="error_extractor",
    )

    return {
        "error": result["error"],
        "logs": result["logs"],
        "description": result["description"],
        "tech_stack": result["tech_stack"],
    }


def risk_analysis_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_risk_prompt(state),
        schema=Risk.model_json_schema(),
        schema_name="risk_analysis",
    )

    return {"risk": result["risk"]}


def error_explanation_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_error_explanation_prompt(state),
        schema=Explanation.model_json_schema(),
        schema_name="error_explanation",
    )

    return {"explanation": result["explanation"]}


def error_prevention_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_error_prevention_prompt(state),
        schema=Prevention.model_json_schema(),
        schema_name="error_prevention",
    )

    return {"prevention": result["prevention"]}


def route_by_risk_node(state: ErrorState) -> str:

    if state["risk"] == "Low":
        return "skip"

    return "analyze"


def classify_error_node(state: ErrorState) -> dict:

    result = classify_error(state["raw_text"])

    return {
        "category": result["category"],
        "confidence": result["confidence"],
    }


def route_by_category_node(state: ErrorState) -> str:

    category = state["category"]

    if category == "ignore":
        return "ignore"

    if category == "command_error":
        return "quick_fix"

    return "detailed_analysis"
