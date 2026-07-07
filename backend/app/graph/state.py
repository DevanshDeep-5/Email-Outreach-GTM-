"""LangGraph state definition — the single object passed through the workflow."""

from typing import Optional
from typing_extensions import TypedDict


class CompanyData(TypedDict):
    pdl_id: str
    name: str
    website: str
    industry: str
    employee_count: Optional[int]
    funding_stage: str
    # populated as workflow progresses
    db_id: Optional[str]
    website_content: Optional[str]
    tavily_summary: Optional[str]
    recent_news: Optional[str]
    company_summary: Optional[str]
    products: Optional[str]
    business_model: Optional[str]
    target_market: Optional[str]
    pain_points: Optional[str]
    growth_signals: Optional[str]
    sales_opportunities: Optional[str]
    outreach_angle: Optional[str]
    value_proposition: Optional[str]
    contacts: Optional[list[dict]]
    intent_score: Optional[int]
    intent_reasoning: Optional[str]
    intent_signals: Optional[list[str]]
    email_subject: Optional[str]
    cold_email: Optional[str]
    cta: Optional[str]
    follow_up_1: Optional[str]
    follow_up_2: Optional[str]
    break_up_email: Optional[str]
    personalization_notes: Optional[str]


class WorkflowState(TypedDict):
    # Campaign config
    campaign_id: str
    campaign_name: str
    industry: Optional[str]
    country: Optional[str]
    employee_min: Optional[int]
    employee_max: Optional[int]
    funding_stage: Optional[str]
    hiring_keywords: list[str]
    technology_keywords: list[str]
    company_keywords: list[str]
    exclude_keywords: list[str]
    target_personas: list[str]
    num_leads: int

    # Runtime
    companies: list[CompanyData]
    current_company_index: int
    errors: list[str]
    export_path: Optional[str]
