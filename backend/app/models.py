import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db import Base


class CampaignStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    industry = Column(String)
    country = Column(String)
    employee_min = Column(Integer)
    employee_max = Column(Integer)
    funding_stage = Column(String)
    hiring_keywords = Column(ARRAY(String), default=[])
    technology_keywords = Column(ARRAY(String), default=[])
    company_keywords = Column(ARRAY(String), default=[])
    exclude_keywords = Column(ARRAY(String), default=[])
    target_personas = Column(ARRAY(String), default=[])
    num_leads = Column(Integer, nullable=False)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.pending)
    current_node = Column(String, default="")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    companies = relationship("Company", back_populates="campaign", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="campaign", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    website = Column(String)
    industry = Column(String)
    employee_count = Column(Integer)
    funding_stage = Column(String)
    provider_id = Column("apollo_id", String)  # formerly apollo_id, now stores PDL company id
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="companies")
    research = relationship("Research", back_populates="company", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    intent_score = relationship("IntentScore", back_populates="company", uselist=False, cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="company", cascade="all, delete-orphan")


class Research(Base):
    __tablename__ = "research"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    website_content = Column(Text)
    tavily_summary = Column(Text)
    recent_news = Column(Text)
    company_summary = Column(Text)
    products = Column(Text)
    business_model = Column(Text)
    target_market = Column(Text)
    pain_points = Column(Text)
    growth_signals = Column(Text)
    sales_opportunities = Column(Text)
    outreach_angle = Column(Text)
    value_proposition = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="research")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String)
    title = Column(String)
    department = Column(String)
    seniority = Column(String)
    email = Column(String)
    email_verified = Column(Boolean, default=False)
    verification_source = Column(String)
    confidence_score = Column(Float)
    data_source = Column(String)
    linkedin_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="contacts")
    emails = relationship("Email", back_populates="contact")


class IntentScore(Base):
    __tablename__ = "intent_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
    reasoning = Column(Text)
    signals = Column(ARRAY(String), default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="intent_score")


class Email(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)
    subject = Column(Text)
    cold_email = Column(Text)
    cta = Column(Text)
    follow_up_1 = Column(Text)
    follow_up_2 = Column(Text)
    break_up_email = Column(Text)
    personalization_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="emails")
    contact = relationship("Contact", back_populates="emails")


class Export(Base):
    __tablename__ = "exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    file_path = Column(String)
    row_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="exports")
