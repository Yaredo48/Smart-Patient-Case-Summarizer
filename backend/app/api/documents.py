from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User, Patient, Document
from app.schemas import DocumentResponse, DocumentCreate
from app.services.file_storage import create_file_storage_service
from app.services.ocr_service import ocr_service
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

file_storage = create_file_storage_service(settings.UPLOAD_DIR)


async def process_document_background(document_id: UUID, db: Session):
    """Background task to process document (OCR extraction)."""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found")
            return
        
        # Update status to processing
        document.processing_status = "processing"
        db.commit()
        
        # Extract text using OCR
        file_extension = document.file_name.split('.')[-1].lower()
        extracted_text = ocr_service.extract_text_from_file(
            document.file_path,
            file_extension
        )
        
        # Update document with extracted text
        document.ocr_text = extracted_text
        document.processed = True
        document.processing_status = "completed"
        db.commit()
        
        logger.info(f"Successfully processed document {document_id}")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.processing_status = "failed"
            document.error_message = str(e)
            db.commit()


@router.post("/upload/{patient_id}", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    patient_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for a patient."""
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Validate file type
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'doc', 'docx']
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Save file
    file_path, saved_size = await file_storage.save_file(
        file.file,
        file.filename,
        str(patient_id)
    )
    
    # Create document record
    new_document = Document(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        file_name=file.filename,
        file_type=file_extension,
        file_path=file_path,
        file_size=saved_size,
        processing_status="pending"
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    # Add background task to process document
    # Note: In production, use Celery for this
    background_tasks.add_task(process_document_background, new_document.id, db)
    
    return new_document


@router.get("/patient/{patient_id}", response_model=List[DocumentResponse])
def get_patient_documents(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a patient."""
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    documents = db.query(Document).filter(Document.patient_id == patient_id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from storage
    file_storage.delete_file(document.file_path)
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return None
