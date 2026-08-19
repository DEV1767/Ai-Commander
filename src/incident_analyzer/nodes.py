from langchain_core.messages import ToolMessage

from .llm import structured_call, agent_model
from .prompts import (
    build_error_explanation_prompt,
    build_error_prevention_prompt,
    build_extractor_prompt,
    build_risk_prompt,
    build_quick_fix_prompt,
    build_action_node_prompt,
    build_action_decision_prompt,
)

from .state import (
    ErrorExtractor,
    ErrorState,
    Risk,
    Explanation,
    Prevention,
    QuickFix,
    ActionDecision,
)

from .guardial import classify_error

from .tools.list_file import list_files
from .tools.read_file import read_file
from .tools.edit_file import edit_file
from .tools.search_file import search_files

# tool_register
tool_map = {
    "read_file": read_file,
    "list_files": list_files,
    "search_files": search_files,
    "edit_file": edit_file,
}

# V2 AGENT NODE


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


# V3 - GUARDRAIL FOR ACTION
def action_decision_node(state: ErrorState) -> dict:

    result = structured_call(
        model_name="openai/gpt-oss-120b",
        prompt=build_action_decision_prompt(state),
        schema=ActionDecision.model_json_schema(),
        schema_name="action_decision",
    )

    return {
        "can_fix": result["can_fix"],
        "fix_reason": result["fix_reason"],
    }


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


def route_by_risk_node(state: ErrorState) -> str:

    return "analyze"


# V3 - ROUTE AFTER DECISION
def route_by_can_fix_node(state: ErrorState) -> str:

    if state.get("can_fix"):
        return "action_node"

    return "skip"


# V3 AGENT NODE
def action_node(state: ErrorState) -> dict:

    messages = [{"role": "user", "content": build_action_node_prompt(state)}]

    max_iterations = 10

    executed_tools = set()

    tools_used = []

    for _ in range(max_iterations):

        response = agent_model.invoke(messages)

        if not response.tool_calls:
            return {
                "action_response": response.content,
                "tool_used": tools_used,
            }

        messages.append(response)

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tool_signature = (tool_name, str(sorted(tool_args.items())))

            if tool_signature in executed_tools:

                print("\n--- DUPLICATE TOOL BLOCKED ---")
                print(tool_name)
                print(tool_args)

                messages.append(
                    ToolMessage(
                        content=(
                            f"You already called {tool_name} "
                            f"with the same arguments. "
                            f"Do NOT call it again. "
                            f"Use another tool or provide your conclusion."
                        ),
                        tool_call_id=tool_call["id"],
                    )
                )

                continue

            executed_tools.add(tool_signature)

            tool = tool_map.get(tool_name)

            if not tool:

                tool_result = f"Unknown tool: {tool_name}"

            else:

                tool_result = tool.invoke(tool_args)

                if tool_name not in tools_used:
                    tools_used.append(tool_name)

            print("\n--- TOOL USED ---")
            print(tool_name)

            print("\n--- TOOL ARGS ---")
            print(tool_args)

            print("\n--- TOOL RESULT ---")
            print(tool_result)
            messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
            )

    return {
        "action_response": (
            "Agent reached the maximum tool-call limit "
            "before completing the investigation."
        ),
        "tool_used": tools_used,
    }
