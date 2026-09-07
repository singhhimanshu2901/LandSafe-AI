"""
Phase 11: Citizen & field reporting endpoints.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.field_report import FieldReport
from app.schemas.report import FieldReportCreate, FieldReportOut

router = APIRouter(prefix="/reports", tags=["reports"])

from app.api.auth import get_current_user, get_current_admin_user
from app.models.user import User
from pydantic import BaseModel

VALID_CATEGORIES = {"LANDSLIDE", "ROAD_BLOCKAGE", "FLASH_FLOOD", "SLOPE_FAILURE", "FALLEN_TREE", "OTHER"}
VALID_STATUSES = {"NEW", "UNDER REVIEW", "VERIFIED", "ASSIGNED", "IN PROGRESS", "RESOLVED"}

def _to_out(r: FieldReport) -> FieldReportOut:
    point = to_shape(r.geometry)
    return FieldReportOut(
        id=r.id, user_id=r.user_id, lat=point.y, lon=point.x, category=r.category,
        severity=r.severity, description=r.description, media_ref=r.media_ref,
        status=r.status, created_at=r.created_at,
    )

@router.post("", response_model=FieldReportOut)
def create_report(payload: FieldReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"category must be one of {VALID_CATEGORIES}")
    try:
        geom = WKTElement(f"POINT({payload.lon} {payload.lat})", srid=4326)
        report = FieldReport(
            user_id=user.id, geometry=geom, category=payload.category,
            severity=payload.severity, description=payload.description,
            media_ref=payload.media_ref, status="NEW",
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return _to_out(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create report: {e}")

@router.get("", response_model=list[FieldReportOut])
def list_reports(
    status: str | None = None,
    category: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(FieldReport)
    if status:
        q = q.filter(FieldReport.status == status)
    if category:
        q = q.filter(FieldReport.category == category)
    results = q.order_by(FieldReport.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_out(r) for r in results]

class StatusUpdate(BaseModel):
    status: str
    resolution_notes: str | None = None

@router.patch("/{report_id}/status", response_model=FieldReportOut)
def update_report_status(report_id: uuid.UUID, payload: StatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")
    report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = payload.status
    if payload.resolution_notes:
        report.description = str(report.description or "") + f"\n\n[Admin Note]: {payload.resolution_notes}"
    db.commit()
    db.refresh(report)
    return _to_out(report)

from fastapi import UploadFile, File
import requests
from app.core.config import settings
import os

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.post("/{report_id}/evidence")
def upload_evidence(
    report_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Validate report ownership
    report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != user.id and user.role not in {"district_admin", "state_admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Not authorized to attach evidence to this report")
        
    # File Validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, WEBP allowed.")
        
    file_bytes = file.file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB")

    # Safe unique filename
    ext = file.content_type.split("/")[-1]
    safe_filename = f"{uuid.uuid4()}.{ext}"
    storage_path = f"{user.id}/{report_id}/{safe_filename}"
    
    # Supabase REST API Upload
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=503, detail="Storage service is not configured on the server")
        
    url = f"{settings.SUPABASE_URL}/storage/v1/object/incident-evidence/{storage_path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": file.content_type
    }
    
    res = requests.post(url, headers=headers, data=file_bytes)
    
    # Depending on configuration, if the bucket doesn't exist, it might 404 or 400.
    if res.status_code >= 400:
        # In a real environment, we'd log `res.text`
        raise HTTPException(status_code=502, detail="Failed to upload evidence to storage provider")
        
    # Store reference
    report.media_ref = storage_path
    db.commit()
    db.refresh(report)
    return {"message": "Evidence uploaded successfully", "media_ref": storage_path}

from fastapi.responses import StreamingResponse

@router.get("/{report_id}/evidence")
def get_evidence(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    report = db.query(FieldReport).filter(FieldReport.id == report_id).first()
    if not report or not report.media_ref:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    if report.user_id != user.id and user.role not in {"district_admin", "state_admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Not authorized to view this evidence")
        
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=503, detail="Storage service is not configured")
        
    # Backend mediated download (keeps bucket private, prevents public URL exposure)
    url = f"{settings.SUPABASE_URL}/storage/v1/object/authenticated/incident-evidence/{report.media_ref}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
    }
    
    # We will just proxy the image binary back to the client
    # In production with large files, streaming is preferred
    res = requests.get(url, headers=headers, stream=True)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to retrieve evidence from storage provider")
        
    return StreamingResponse(res.raw, media_type=res.headers.get("Content-Type", "image/jpeg"))
