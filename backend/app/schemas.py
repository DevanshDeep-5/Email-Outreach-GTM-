from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# ─── Campaign ───────────────────────────────────────────────────────────────

DEFAULT_PERSONAS = [
    "Founder",
    "CEO",
    "VP Sales",
    "Head of Sales",
    "Revenue Operations",
    "Growth Lead",
    "Marketing Director",
    "Director of Sales",
    "Sales Manager",
]


class CampaignCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_min: Optional[int] = None
    employee_max: Optional[int] = None
    funding_stage: Optional[str] = None
    hiring_keywords: list[str] = []
    technology_keywords: list[str] = []
    company_keywords: list[str] = []
    exclude_keywords: list[str] = []
    target_personas: list[str] = DEFAULT_PERSONAS
    num_leads: int


class CampaignOut(BaseModel):
    id: UUID
    name: str
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
    status: str
    current_node: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignStats(BaseModel):
    campaign: CampaignOut
    companies_found: int
    companies_processed: int
    contacts_found: int
    emails_generated: int
    export_ready: bool


# ─── Company ─────────────────────────────────────────────────────────────────

class CompanyOut(BaseModel):
    id: UUID
    campaign_id: UUID
    name: str
    website: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    funding_stage: Optional[str]
    provider_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ResearchOut(BaseModel):
    id: UUID
    company_id: UUID
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
    created_at: datetime

    model_config = {"from_attributes": True}


class IntentScoreOut(BaseModel):
    id: UUID
    company_id: UUID
    score: int
    reasoning: Optional[str]
    signals: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyDetail(BaseModel):
    company: CompanyOut
    research: Optional[ResearchOut]
    intent_score: Optional[IntentScoreOut]
    contacts: list["ContactOut"]
    emails: list["EmailOut"]


# ─── Contact ─────────────────────────────────────────────────────────────────

class ContactOut(BaseModel):
    id: UUID
    company_id: UUID
    name: Optional[str]
    title: Optional[str]
    department: Optional[str]
    seniority: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    verification_source: Optional[str]
    confidence_score: Optional[float]
    data_source: Optional[str]
    linkedin_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Email ───────────────────────────────────────────────────────────────────

class EmailOut(BaseModel):
    id: UUID
    company_id: UUID
    contact_id: Optional[UUID]
    subject: Optional[str]
    cold_email: Optional[str]
    cta: Optional[str]
    follow_up_1: Optional[str]
    follow_up_2: Optional[str]
    break_up_email: Optional[str]
    personalization_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailUpdate(BaseModel):
    subject: Optional[str] = None
    cold_email: Optional[str] = None
    cta: Optional[str] = None
    follow_up_1: Optional[str] = None
    follow_up_2: Optional[str] = None
    break_up_email: Optional[str] = None
    personalization_notes: Optional[str] = None


# ─── Export ──────────────────────────────────────────────────────────────────

class ExportOut(BaseModel):
    id: UUID
    campaign_id: UUID
    file_path: Optional[str]
    row_count: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_campaigns: int
    total_companies: int
    total_contacts: int
    total_emails: int
    export_count: int
    recent_campaigns: list[CampaignOut]
