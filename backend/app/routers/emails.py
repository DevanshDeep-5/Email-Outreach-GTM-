from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Email
from app.schemas import EmailOut, EmailUpdate
from app.services import llm
from app.models import Company, Contact

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("/", response_model=list[EmailOut])
def list_emails(campaign_id: str = None, company_id: str = None, db: Session = Depends(get_db)):
    q = db.query(Email)
    if company_id:
        q = q.filter(Email.company_id == company_id)
    if campaign_id:
        company_ids = [
            c.id for c in db.query(Company).filter(Company.campaign_id == campaign_id).all()
        ]
        q = q.filter(Email.company_id.in_(company_ids))
    return q.order_by(Email.created_at.desc()).all()


@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: str, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.put("/{email_id}", response_model=EmailOut)
def update_email(email_id: str, payload: EmailUpdate, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(email, field, value)

    db.commit()
    db.refresh(email)
    return email


@router.post("/{email_id}/regenerate", response_model=EmailOut)
def regenerate_email(email_id: str, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    company = db.query(Company).filter(Company.id == email.company_id).first()
    contact = db.query(Contact).filter(Contact.id == email.contact_id).first() if email.contact_id else None
    research = company.research if company else None

    if not company or not research:
        raise HTTPException(status_code=400, detail="Company research not found")

    analysis = {
        "pain_points": research.pain_points or "",
        "outreach_angle": research.outreach_angle or "",
        "value_proposition": research.value_proposition or "",
        "growth_signals": research.growth_signals or "",
    }
    intent_signals = company.intent_score.signals if company.intent_score else []

    email_set = llm.generate_cold_email(
        company_name=company.name,
        contact_name=contact.name if contact else "there",
        contact_title=contact.title if contact else "",
        company_analysis=analysis,
        intent_signals=intent_signals,
    )
    followups = llm.generate_followups(
        company_name=company.name,
        contact_name=contact.name if contact else "there",
        cold_email_subject=email_set.subject,
        cold_email_body=email_set.cold_email,
    )

    email.subject = email_set.subject
    email.cold_email = email_set.cold_email
    email.cta = email_set.cta
    email.personalization_notes = email_set.personalization_notes
    email.follow_up_1 = followups.follow_up_1
    email.follow_up_2 = followups.follow_up_2
    email.break_up_email = followups.break_up_email

    db.commit()
    db.refresh(email)
    return email
