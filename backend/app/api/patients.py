from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User, Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientDetail

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new patient."""
    # Check if MRN already exists
    existing_patient = db.query(Patient).filter(Patient.mrn == patient_data.mrn).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this MRN already exists"
        )
    
    # Create new patient
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return new_patient


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all patients with optional search."""
    query = db.query(Patient)
    
    # Apply search filter if provided
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter)) |
            (Patient.mrn.ilike(search_filter))
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientDetail)
def get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific patient by ID with all related data."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a patient's information."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a patient."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    db.delete(patient)
    db.commit()
    
    return None
