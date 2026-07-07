"""LangGraph workflow assembly."""

from langgraph.graph import StateGraph, END

from app.graph.state import WorkflowState
from app.graph.nodes import (
    campaign_planner,
    company_finder,
    website_researcher,
    web_researcher,
    company_analyzer,
    contact_finder,
    intent_analyzer,
    email_generator,
    followup_generator,
    csv_exporter,
)


def build_workflow() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("campaign_planner", campaign_planner)
    graph.add_node("company_finder", company_finder)
    graph.add_node("website_researcher", website_researcher)
    graph.add_node("web_researcher", web_researcher)
    graph.add_node("company_analyzer", company_analyzer)
    graph.add_node("contact_finder", contact_finder)
    graph.add_node("intent_analyzer", intent_analyzer)
    graph.add_node("email_generator", email_generator)
    graph.add_node("followup_generator", followup_generator)
    graph.add_node("csv_exporter", csv_exporter)

    graph.set_entry_point("campaign_planner")

    graph.add_edge("campaign_planner", "company_finder")
    graph.add_edge("company_finder", "website_researcher")
    graph.add_edge("website_researcher", "web_researcher")
    graph.add_edge("web_researcher", "company_analyzer")
    graph.add_edge("company_analyzer", "contact_finder")
    graph.add_edge("contact_finder", "intent_analyzer")
    graph.add_edge("intent_analyzer", "email_generator")
    graph.add_edge("email_generator", "followup_generator")
    graph.add_edge("followup_generator", "csv_exporter")
    graph.add_edge("csv_exporter", END)

    return graph.compile()


# Compiled workflow — import and call .invoke()
workflow = build_workflow()
