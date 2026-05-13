from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.calibration import CalibrationAgency
from app.models.user import User
from app.schemas import CalibrationAgencyCreate, CalibrationAgencyResponse
from app.utils.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[CalibrationAgencyResponse])
def list_agencies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(CalibrationAgency).all()

@router.get("/{agency_id}", response_model=CalibrationAgencyResponse)
def get_agency(agency_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agency = db.query(CalibrationAgency).filter(CalibrationAgency.id == agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="检测院不存在")
    return agency

@router.post("/", response_model=CalibrationAgencyResponse)
def create_agency(
    agency: CalibrationAgencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_agency = CalibrationAgency(**agency.model_dump())
    db.add(db_agency)
    db.commit()
    db.refresh(db_agency)
    return db_agency

@router.put("/{agency_id}", response_model=CalibrationAgencyResponse)
def update_agency(
    agency_id: int,
    agency: CalibrationAgencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_agency = db.query(CalibrationAgency).filter(CalibrationAgency.id == agency_id).first()
    if not db_agency:
        raise HTTPException(status_code=404, detail="检测院不存在")
    for key, value in agency.model_dump(exclude_unset=True).items():
        setattr(db_agency, key, value)
    db.commit()
    db.refresh(db_agency)
    return db_agency

@router.delete("/{agency_id}")
def delete_agency(
    agency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    agency = db.query(CalibrationAgency).filter(CalibrationAgency.id == agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="检测院不存在")
    db.delete(agency)
    db.commit()
    return {"message": "删除成功"}
