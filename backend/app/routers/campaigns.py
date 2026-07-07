import threading
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Campaign, Company, Contact, Email, Export, CampaignStatus
from app.schemas import (
    CampaignCreate, CampaignOut, CampaignStats, DashboardStats
)
from app.graph.workflow import workflow

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


def _run_workflow(campaign_id: str, initial_state: dict):
    """Run the LangGraph workflow in a background thread."""
    from app.db import SessionLocal
    from app.models import Campaign, CampaignStatus

    try:
        workflow.invoke(initial_state)
    except Exception as e:
        db = SessionLocal()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = CampaignStatus.failed
                campaign.error_message = str(e)
                db.commit()
        finally:
            db.close()


@router.get("/", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.post("/", response_model=CampaignOut)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(
        id=uuid.uuid4(),
        **payload.model_dump(),
        status=CampaignStatus.pending,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    initial_state = {
        "campaign_id": str(campaign.id),
        "campaign_name": campaign.name,
        "industry": campaign.industry,
        "country": campaign.country,
        "employee_min": campaign.employee_min,
        "employee_max": campaign.employee_max,
        "funding_stage": campaign.funding_stage,
        "hiring_keywords": campaign.hiring_keywords or [],
        "technology_keywords": campaign.technology_keywords or [],
        "company_keywords": campaign.company_keywords or [],
        "exclude_keywords": campaign.exclude_keywords or [],
        "target_personas": campaign.target_personas or [],
        "num_leads": campaign.num_leads,
        "companies": [],
        "current_company_index": 0,
        "errors": [],
        "export_path": None,
    }

    thread = threading.Thread(
        target=_run_workflow,
        args=(str(campaign.id), initial_state),
        daemon=True,
    )
    thread.start()

    return campaign


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    from app.models import Company, Contact, Email, Export

    total_campaigns = db.query(Campaign).count()
    total_companies = db.query(Company).count()
    total_contacts = db.query(Contact).count()
    total_emails = db.query(Email).count()
    export_count = db.query(Export).count()
    recent = db.query(Campaign).order_by(Campaign.created_at.desc()).limit(5).all()

    return DashboardStats(
        total_campaigns=total_campaigns,
        total_companies=total_companies,
        total_contacts=total_contacts,
        total_emails=total_emails,
        export_count=export_count,
        recent_campaigns=[CampaignOut.model_validate(c) for c in recent],
    )


@router.get("/{campaign_id}", response_model=CampaignStats)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    companies = db.query(Company).filter(Company.campaign_id == campaign_id).all()
    company_ids = [c.id for c in companies]
    contacts_count = db.query(Contact).filter(Contact.company_id.in_(company_ids)).count()
    emails_count = db.query(Email).filter(Email.company_id.in_(company_ids)).count()
    export_ready = db.query(Export).filter(Export.campaign_id == campaign_id).count() > 0

    processed = sum(
        1 for c in companies
        if db.query(Email).filter(Email.company_id == c.id).count() > 0
    )

    return CampaignStats(
        campaign=CampaignOut.model_validate(campaign),
        companies_found=len(companies),
        companies_processed=processed,
        contacts_found=contacts_count,
        emails_generated=emails_count,
        export_ready=export_ready,
    )


@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    return {"ok": True}
