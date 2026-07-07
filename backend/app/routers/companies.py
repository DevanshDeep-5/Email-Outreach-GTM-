from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Company, Contact, Email
from app.schemas import CompanyOut, CompanyDetail, ResearchOut, IntentScoreOut, ContactOut, EmailOut

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyOut])
def list_companies(campaign_id: str = None, db: Session = Depends(get_db)):
    q = db.query(Company)
    if campaign_id:
        q = q.filter(Company.campaign_id == campaign_id)
    return q.order_by(Company.created_at.desc()).all()


@router.get("/{company_id}", response_model=CompanyDetail)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    research = company.research
    intent_score = company.intent_score
    contacts = company.contacts
    emails = company.emails

    return CompanyDetail(
        company=CompanyOut.model_validate(company),
        research=ResearchOut.model_validate(research) if research else None,
        intent_score=IntentScoreOut.model_validate(intent_score) if intent_score else None,
        contacts=[ContactOut.model_validate(c) for c in contacts],
        emails=[EmailOut.model_validate(e) for e in emails],
    )
