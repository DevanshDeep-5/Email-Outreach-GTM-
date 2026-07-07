import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Export, Campaign, Company, Contact, Email, IntentScore, Research
from app.schemas import ExportOut

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/", response_model=list[ExportOut])
def list_exports(db: Session = Depends(get_db)):
    return db.query(Export).order_by(Export.created_at.desc()).all()


@router.get("/{export_id}/download")
def download_export(export_id: str, db: Session = Depends(get_db)):
    export = db.query(Export).filter(Export.id == export_id).first()
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    if not export.file_path or not os.path.exists(export.file_path):
        raise HTTPException(status_code=404, detail="CSV file not found on disk")

    return FileResponse(
        path=export.file_path,
        media_type="text/csv",
        filename=os.path.basename(export.file_path),
    )


@router.get("/campaign/{campaign_id}", response_model=list[ExportOut])
def campaign_exports(campaign_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Export)
        .filter(Export.campaign_id == campaign_id)
        .order_by(Export.created_at.desc())
        .all()
    )
