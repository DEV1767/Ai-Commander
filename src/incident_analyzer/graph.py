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
)

from .state import ErrorState


def build_graph():

    graph = StateGraph(ErrorState)

    # Nodes
    graph.add_node("classify_error", classify_error_node)
    graph.add_node("quick_fix", quick_fix_node)
    graph.add_node("Extractor", extractor_node)
    graph.add_node("risk_analysis", risk_analysis_node)
    graph.add_node("error_explanation", error_explanation_node)
    graph.add_node("error_prevention", error_prevention_node)

    # START → Guardrail
    graph.add_edge(START, "classify_error")

    # Guardrail routing
    graph.add_conditional_edges(
        "classify_error",
        route_by_category_node,
        {
            "ignore": END,
            "quick_fix": "quick_fix",
            "detailed_analysis": "Extractor",
        },
    )

    # Quick command fix → END
    graph.add_edge("quick_fix", END)

    # Detailed analysis pipeline
    graph.add_edge("Extractor", "risk_analysis")

    # Risk routing
    graph.add_conditional_edges(
        "risk_analysis",
        route_by_risk_node,
        {
            "skip": END,
            "analyze": "error_explanation",
        },
    )

    # Explanation → Prevention → END
    graph.add_edge("error_explanation", "error_prevention")

    graph.add_edge("error_prevention", END)

    return graph.compile()
