from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User, Patient, Document, Summary
from app.schemas import SummaryResponse, SummaryCreate
from app.services.summarization_service import create_summarization_service
from app.core.config import settings

router = APIRouter(prefix="/summaries", tags=["Summaries"])
logger = logging.getLogger(__name__)


async def generate_summary_background(patient_id: UUID, user_id: UUID, db: Session):
   """Background task to generate patient summary."""
    try:
        # Get patient info
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            logger.error(f"Patient {patient_id} not found")
            return
        
        # Get all processed documents for this patient
        documents = db.query(Document).filter(
            Document.patient_id == patient_id,
            Document.processed == True
        ).all()
        
        if not documents:
            logger.warning(f"No processed documents found for patient {patient_id}")
            return
        
        # Extract all document texts
        documents_text = [doc.ocr_text for doc in documents if doc.ocr_text]
        
        if not documents_text:
            logger.warning(f"No OCR text available for patient {patient_id}")
            return
        
        # Prepare patient info
        patient_info = {
            "mrn": patient.mrn,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender
        }
        
        # Create summarization service
        summarizer = create_summarization_service(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        
        # Generate summary
        summary_data = summarizer.generate_summary(
            patient_info=patient_info,
            documents_text=documents_text
        )
        
        # Mark previous summaries as not latest
        db.query(Summary).filter(
            Summary.patient_id == patient_id,
            Summary.is_latest == True
        ).update({"is_latest": False})
        
        # Create new summary
        new_summary = Summary(
            patient_id=patient_id,
            created_by=user_id,
            summary_text=summary_data["summary_text"],
            red_flags=summary_data["red_flags"],
            lab_results=summary_data["lab_results"],
            medications=summary_data["medications"],
            is_latest=True
        )
        
        db.add(new_summary)
        db.commit()
        
        logger.info(f"Successfully generated summary for patient {patient_id}")
        
    except Exception as e:
        logger.error(f"Error generating summary for patient {patient_id}: {str(e)}")


@router.post("/generate/{patient_id}", status_code=status.HTTP_202_ACCEPTED)
async def generate_summary(
    patient_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a summary for a patient (async process)."""
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if there are processed documents
    doc_count = db.query(Document).filter(
        Document.patient_id == patient_id,
        Document.processed == True
    ).count()
    
    if doc_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processed documents available for this patient"
        )
    
    # Add background task
    background_tasks.add_task(
        generate_summary_background,
        patient_id,
        current_user.id,
        db
    )
    
    return {"message": "Summary generation started", "patient_id": str(patient_id)}


@router.get("/patient/{patient_id}", response_model=List[SummaryResponse])
def get_patient_summaries(
    patient_id: UUID,
    latest_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all summaries for a patient."""
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    query = db.query(Summary).filter(Summary.patient_id == patient_id)
    
    if latest_only:
        query = query.filter(Summary.is_latest == True)
    
    summaries = query.order_by(Summary.created_at.desc()).all()
    return summaries


@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(
    summary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific summary."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_summary(
    summary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a summary."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    db.delete(summary)
    db.commit()
    
    return None
