"""LangGraph nodes — each function has exactly one responsibility."""

import uuid
import os
import pandas as pd
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.graph.state import WorkflowState, CompanyData
from app.models import (
    Campaign, Company, Research, Contact, IntentScore, Email, Export, CampaignStatus
)
from app.services import firecrawl, tavily, llm
from app.services import people_data_labs as pdl
from app.services import contacts as contact_service
from app.db import SessionLocal


def _get_db() -> Session:
    return SessionLocal()


def _update_campaign_node(campaign_id: str, node_name: str):
    db = _get_db()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.current_node = node_name
            db.commit()
    finally:
        db.close()


# ─── Node 1: Campaign Planner ─────────────────────────────────────────────────

def campaign_planner(state: WorkflowState) -> WorkflowState:
    """Validate campaign config and set workflow status to running."""
    _update_campaign_node(state["campaign_id"], "campaign_planner")

    db = _get_db()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == state["campaign_id"]).first()
        if campaign:
            campaign.status = CampaignStatus.running
            db.commit()
    finally:
        db.close()

    return {
        **state,
        "companies": [],
        "current_company_index": 0,
        "errors": [],
        "export_path": None,
    }


# ─── Node 2: Company Finder ───────────────────────────────────────────────────

def company_finder(state: WorkflowState) -> WorkflowState:
    """Use People Data Labs to find companies matching the ICP."""
    _update_campaign_node(state["campaign_id"], "company_finder")

    keywords = (
        state.get("hiring_keywords", [])
        + state.get("technology_keywords", [])
        + state.get("company_keywords", [])
    )

    try:
        raw_companies = pdl.search_companies(
            industry=state.get("industry"),
            country=state.get("country"),
            employee_min=state.get("employee_min"),
            employee_max=state.get("employee_max"),
            funding_stage=state.get("funding_stage"),
            keywords=keywords,
            limit=state["num_leads"],
        )
    except Exception as e:
        raw_companies = []
        state["errors"].append(f"PDL company search failed: {str(e)}")

    exclude = [k.lower() for k in state.get("exclude_keywords", [])]
    filtered = [
        c for c in raw_companies
        if not any(ex in (c.get("name", "") + c.get("industry", "")).lower() for ex in exclude)
    ]

    companies: list[CompanyData] = []
    db = _get_db()
    try:
        for c in filtered[: state["num_leads"]]:
            company = Company(
                id=uuid.uuid4(),
                campaign_id=state["campaign_id"],
                name=c["name"],
                website=c.get("website", ""),
                industry=c.get("industry", ""),
                employee_count=c.get("employee_count"),
                funding_stage=c.get("funding_stage", ""),
                provider_id=c.get("pdl_id", ""),
            )
            db.add(company)
            db.flush()

            entry: CompanyData = {
                "pdl_id": c.get("pdl_id", ""),
                "name": c["name"],
                "website": c.get("website", ""),
                "industry": c.get("industry", ""),
                "employee_count": c.get("employee_count"),
                "funding_stage": c.get("funding_stage", ""),
                "db_id": str(company.id),
                "website_content": None,
                "tavily_summary": None,
                "recent_news": None,
                "company_summary": None,
                "products": None,
                "business_model": None,
                "target_market": None,
                "pain_points": None,
                "growth_signals": None,
                "sales_opportunities": None,
                "outreach_angle": None,
                "value_proposition": None,
                "contacts": None,
                "intent_score": None,
                "intent_reasoning": None,
                "intent_signals": None,
                "email_subject": None,
                "cold_email": None,
                "cta": None,
                "follow_up_1": None,
                "follow_up_2": None,
                "break_up_email": None,
                "personalization_notes": None,
            }
            companies.append(entry)

        db.commit()
    finally:
        db.close()

    return {**state, "companies": companies}


# ─── Node 3: Website Researcher ──────────────────────────────────────────────

def website_researcher(state: WorkflowState) -> WorkflowState:
    """Scrape company websites using Firecrawl."""
    _update_campaign_node(state["campaign_id"], "website_researcher")

    updated_companies = []
    for company in state["companies"]:
        website = company.get("website", "")
        content = ""
        if website:
            try:
                content = firecrawl.scrape_website(website)
            except Exception as e:
                state["errors"].append(f"Firecrawl failed for {company['name']}: {str(e)}")

        updated_companies.append({**company, "website_content": content})

    return {**state, "companies": updated_companies}


# ─── Node 4: Web Researcher ───────────────────────────────────────────────────

def web_researcher(state: WorkflowState) -> WorkflowState:
    """Use Tavily to research news, funding, and hiring signals."""
    _update_campaign_node(state["campaign_id"], "web_researcher")

    updated_companies = []
    for company in state["companies"]:
        try:
            research = tavily.research_company(
                company_name=company["name"],
                website=company.get("website", ""),
            )
            updated_companies.append({
                **company,
                "tavily_summary": research["tavily_summary"],
                "recent_news": research["recent_news"],
            })
        except Exception as e:
            state["errors"].append(f"Tavily failed for {company['name']}: {str(e)}")
            updated_companies.append(company)

    return {**state, "companies": updated_companies}


# ─── Node 5: Company Analyzer ─────────────────────────────────────────────────

def company_analyzer(state: WorkflowState) -> WorkflowState:
    """Use LLM to analyze each company and extract sales intelligence."""
    _update_campaign_node(state["campaign_id"], "company_analyzer")

    updated_companies = []
    for company in state["companies"]:
        try:
            analysis = llm.analyze_company(
                company_name=company["name"],
                website_content=company.get("website_content", "") or "",
                tavily_summary=company.get("tavily_summary", "") or "",
            )
            updated = {
                **company,
                "company_summary": analysis.company_summary,
                "products": analysis.products,
                "business_model": analysis.business_model,
                "target_market": analysis.target_market,
                "pain_points": analysis.pain_points,
                "growth_signals": analysis.growth_signals,
                "sales_opportunities": analysis.sales_opportunities,
                "outreach_angle": analysis.outreach_angle,
                "value_proposition": analysis.value_proposition,
            }
            updated_companies.append(updated)
        except Exception as e:
            state["errors"].append(f"LLM analysis failed for {company['name']}: {str(e)}")
            updated_companies.append(company)

    # Persist research to DB
    db = _get_db()
    try:
        for company in updated_companies:
            if not company.get("db_id"):
                continue
            research = Research(
                company_id=company["db_id"],
                website_content=company.get("website_content", ""),
                tavily_summary=company.get("tavily_summary", ""),
                recent_news=company.get("recent_news", ""),
                company_summary=company.get("company_summary", ""),
                products=company.get("products", ""),
                business_model=company.get("business_model", ""),
                target_market=company.get("target_market", ""),
                pain_points=company.get("pain_points", ""),
                growth_signals=company.get("growth_signals", ""),
                sales_opportunities=company.get("sales_opportunities", ""),
                outreach_angle=company.get("outreach_angle", ""),
                value_proposition=company.get("value_proposition", ""),
            )
            db.add(research)
        db.commit()
    finally:
        db.close()

    return {**state, "companies": updated_companies}


# ─── Node 6: Contact Finder (People Data Labs) ──────────────────────────────────

def contact_finder(state: WorkflowState) -> WorkflowState:
    """Use People Data Labs (+ Firecrawl fallback) to find decision-maker contacts."""
    _update_campaign_node(state["campaign_id"], "contact_finder")

    target_personas = state.get("target_personas") or []
    updated_companies = []
    db = _get_db()
    try:
        for company in state["companies"]:
            contacts = []
            try:
                raw_contacts = contact_service.find_contacts(
                    company_name=company["name"],
                    website=company.get("website", ""),
                    target_personas=target_personas,
                    limit=10,
                )
                for rc in raw_contacts:
                    contact = Contact(
                        company_id=company["db_id"],
                        name=rc.get("name", ""),
                        title=rc.get("title", ""),
                        department=rc.get("department", ""),
                        seniority=rc.get("seniority", ""),
                        email=rc.get("email", ""),
                        email_verified=rc.get("email_verified", False),
                        verification_source=rc.get("verification_source", ""),
                        confidence_score=rc.get("confidence_score"),
                        data_source=rc.get("data_source", ""),
                        linkedin_url=rc.get("linkedin_url", ""),
                    )
                    db.add(contact)
                    db.flush()
                    contacts.append({**rc, "db_id": str(contact.id)})
            except Exception as e:
                state["errors"].append(f"Contact search failed for {company['name']}: {str(e)}")

            updated_companies.append({**company, "contacts": contacts})

        db.commit()
    finally:
        db.close()

    return {**state, "companies": updated_companies}

# ─── Node 7: Intent Analyzer ──────────────────────────────────────────────────

def intent_analyzer(state: WorkflowState) -> WorkflowState:
    """Score each company's buying intent using the LLM."""
    _update_campaign_node(state["campaign_id"], "intent_analyzer")

    updated_companies = []
    db = _get_db()
    try:
        for company in state["companies"]:
            research_text = "\n".join(filter(None, [
                company.get("tavily_summary", ""),
                company.get("recent_news", ""),
            ]))
            analysis_text = "\n".join(filter(None, [
                company.get("company_summary", ""),
                company.get("growth_signals", ""),
            ]))

            try:
                intent = llm.analyze_intent(
                    company_name=company["name"],
                    research_summary=research_text,
                    company_analysis=analysis_text,
                )
                updated = {
                    **company,
                    "intent_score": intent.score,
                    "intent_reasoning": intent.reasoning,
                    "intent_signals": intent.signals,
                }
            except Exception as e:
                state["errors"].append(f"Intent scoring failed for {company['name']}: {str(e)}")
                updated = company

            if company.get("db_id"):
                score_val = updated.get("intent_score")
                if score_val is not None:
                    score_record = IntentScore(
                        company_id=company["db_id"],
                        score=score_val,
                        reasoning=updated.get("intent_reasoning") or "",
                        signals=updated.get("intent_signals") or [],
                    )
                    db.add(score_record)

            updated_companies.append(updated)

        db.commit()
    finally:
        db.close()

    return {**state, "companies": updated_companies}


# ─── Node 8: Email Generator ──────────────────────────────────────────────────

def email_generator(state: WorkflowState) -> WorkflowState:
    """Generate personalized cold emails for each company."""
    _update_campaign_node(state["campaign_id"], "email_generator")

    updated_companies = []
    for company in state["companies"]:
        contacts = company.get("contacts") or []
        primary = contacts[0] if contacts else {}

        contact_name = primary.get("name", "there")
        contact_title = primary.get("title", "")

        analysis = {
            "pain_points": company.get("pain_points", ""),
            "outreach_angle": company.get("outreach_angle", ""),
            "value_proposition": company.get("value_proposition", ""),
            "growth_signals": company.get("growth_signals", ""),
        }
        intent_signals = company.get("intent_signals") or []

        try:
            email_set = llm.generate_cold_email(
                company_name=company["name"],
                contact_name=contact_name,
                contact_title=contact_title,
                company_analysis=analysis,
                intent_signals=intent_signals,
            )
            updated = {
                **company,
                "email_subject": email_set.subject,
                "cold_email": email_set.cold_email,
                "cta": email_set.cta,
                "personalization_notes": email_set.personalization_notes,
            }
        except Exception as e:
            state["errors"].append(f"Email generation failed for {company['name']}: {str(e)}")
            updated = company

        updated_companies.append(updated)

    return {**state, "companies": updated_companies}


# ─── Node 9: Follow-up Generator ─────────────────────────────────────────────

def followup_generator(state: WorkflowState) -> WorkflowState:
    """Generate follow-up sequence for each company."""
    _update_campaign_node(state["campaign_id"], "followup_generator")

    updated_companies = []
    db = _get_db()
    try:
        for company in state["companies"]:
            contacts = company.get("contacts") or []
            primary = contacts[0] if contacts else {}
            contact_name = primary.get("name", "there")

            try:
                followups = llm.generate_followups(
                    company_name=company["name"],
                    contact_name=contact_name,
                    cold_email_subject=company.get("email_subject", ""),
                    cold_email_body=company.get("cold_email", ""),
                )
                updated = {
                    **company,
                    "follow_up_1": followups.follow_up_1,
                    "follow_up_2": followups.follow_up_2,
                    "break_up_email": followups.break_up_email,
                }
            except Exception as e:
                state["errors"].append(f"Follow-up generation failed for {company['name']}: {str(e)}")
                updated = company

            # Save emails to DB
            if company.get("db_id"):
                contact_db_id = primary.get("db_id") if primary else None
                email_record = Email(
                    company_id=company["db_id"],
                    contact_id=contact_db_id,
                    subject=updated.get("email_subject") or "",
                    cold_email=updated.get("cold_email") or "",
                    cta=updated.get("cta") or "",
                    follow_up_1=updated.get("follow_up_1") or "",
                    follow_up_2=updated.get("follow_up_2") or "",
                    break_up_email=updated.get("break_up_email") or "",
                    personalization_notes=updated.get("personalization_notes") or "",
                )
                db.add(email_record)

            updated_companies.append(updated)

        db.commit()
    finally:
        db.close()

    return {**state, "companies": updated_companies}


# ─── Node 10: CSV Exporter ────────────────────────────────────────────────────

def csv_exporter(state: WorkflowState) -> WorkflowState:
    """Build and save the final CSV export."""
    _update_campaign_node(state["campaign_id"], "csv_exporter")

    rows = []
    for company in state["companies"]:
        contacts = company.get("contacts") or [{}]
        primary = contacts[0] if contacts else {}

        rows.append({
            "Company": company.get("name") or "",
            "Website": company.get("website") or "",
            "Contact Name": primary.get("name") or "",
            "Title": primary.get("title") or "",
            "Department": primary.get("department") or "",
            "Seniority": primary.get("seniority") or "",
            "Email": primary.get("email") or "",
            "Email Verified": primary.get("email_verified", False),
            "Confidence Score": primary.get("confidence_score") or "",
            "Data Source": primary.get("data_source") or "",
            "LinkedIn": primary.get("linkedin_url") or "",
            "Intent Score": company.get("intent_score") if company.get("intent_score") is not None else "",
            "Intent Reason": company.get("intent_reasoning") or "",
            "Subject": company.get("email_subject") or "",
            "Cold Email": company.get("cold_email") or "",
            "Follow-up 1": company.get("follow_up_1") or "",
            "Follow-up 2": company.get("follow_up_2") or "",
            "Break-up Email": company.get("break_up_email") or "",
        })

    df = pd.DataFrame(rows)

    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"campaign_{state['campaign_id'][:8]}_{timestamp}.csv"
    file_path = os.path.join(export_dir, filename)
    df.to_csv(file_path, index=False)

    db = _get_db()
    try:
        export = Export(
            campaign_id=state["campaign_id"],
            file_path=file_path,
            row_count=len(rows),
        )
        db.add(export)

        campaign = db.query(Campaign).filter(Campaign.id == state["campaign_id"]).first()
        if campaign:
            campaign.status = CampaignStatus.completed
            campaign.current_node = "completed"

        db.commit()
    finally:
        db.close()

    return {**state, "export_path": file_path}
