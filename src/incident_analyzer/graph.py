from langgraph.graph import END, START, StateGraph

from .nodes import (
    error_explanation_node,
    error_prevention_node,
    extractor_node,
    risk_analysis_node,
    route_by_risk_node,
    route_by_category_node,
    classify_error_node,
    quick_fix_node,
    action_decision_node,
    action_node,
)

from .state import ErrorState


def build_graph():

    graph = StateGraph(ErrorState)

    # NODES

    graph.add_node("classify_error", classify_error_node)

    graph.add_node("quick_fix", quick_fix_node)

    graph.add_node("Extractor", extractor_node)

    graph.add_node("risk_analysis", risk_analysis_node)

    graph.add_node("error_explanation", error_explanation_node)

    graph.add_node("error_prevention", error_prevention_node)

    # V3 decision node
    graph.add_node("action_decision", action_decision_node)

    # START → GUARDRAIL

    graph.add_edge(START, "classify_error")

    # GUARDRAIL ROUTING

    graph.add_conditional_edges(
        "classify_error",
        route_by_category_node,
        {
            "ignore": END,
            "quick_fix": "quick_fix",
            "detailed_analysis": "Extractor",
        },
    )

    # COMMAND ERROR

    graph.add_edge("quick_fix", END)

    # DETAILED ANALYSIS

    graph.add_edge("Extractor", "risk_analysis")

    # RISK ROUTING
    graph.add_edge("risk_analysis", "error_explanation")
    # V2 ANALYSIS

    graph.add_edge("error_explanation", "error_prevention")

    # V2 → V3 DECISION

    graph.add_edge("error_prevention", "action_decision")

    # V3 DECISION → END

    graph.add_edge("action_decision", END)

    return graph.compile()


def build_correction_graph():
    """
    Runs ONLY when the user clicks the 'Correct' button.
    Does not re-run classify_error, Extractor, risk_analysis,
    error_explanation, error_prevention, or action_decision —
    those already ran once inside build_graph() during /analyze.

    Expects to be invoked with the full state dict returned from
    build_graph(), which must include can_fix=True and the fields
    action_node's prompt depends on (error, logs, description, tech_stack).
    """

    graph = StateGraph(ErrorState)

    graph.add_node("action_node", action_node)

    graph.add_edge(START, "action_node")

    graph.add_edge("action_node", END)

    return graph.compile()
