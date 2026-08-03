from langgraph.graph import END, START, StateGraph

from .nodes import (
    error_explanation_node,
    error_prevention_node,
    extractor_node,
    risk_analysis_node,
    route_by_risk
)
from .state import ErrorState


def build_graph():
    graph = StateGraph(ErrorState)

    graph.add_node("Extractor", extractor_node)
    graph.add_node("risk_analysis", risk_analysis_node)
    graph.add_node("error_explanation", error_explanation_node)
    graph.add_node("error_prevention", error_prevention_node)

    graph.add_edge(START, "Extractor")
    graph.add_edge("Extractor", "risk_analysis")

    graph.add_conditional_edges(
        "risk_analysis",
        route_by_risk,
        {
            "analyze": "error_explanation",
            "skip": END,
        }
    )

    graph.add_edge("risk_analysis", "error_prevention")

    graph.add_edge("error_explanation", END)
    graph.add_edge("error_prevention", END)

    return graph.compile()