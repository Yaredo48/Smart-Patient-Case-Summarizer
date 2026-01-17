from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "doctor"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Patient Schemas
class PatientBase(BaseModel):
    mrn: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    metadata: Optional[dict] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    metadata: Optional[dict] = None


class PatientResponse(PatientBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Document Schemas
class DocumentBase(BaseModel):
    file_name: str
    file_type: str


class DocumentCreate(DocumentBase):
    patient_id: UUID


class DocumentResponse(DocumentBase):
    id: UUID
    patient_id: UUID
    uploaded_by: UUID
    file_size: Optional[int] = None
    processed: bool
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Summary Schemas
class RedFlag(BaseModel):
    category: str
    finding: str
    severity: str  # low, medium, high, critical
    value: Optional[str] = None


class SummaryBase(BaseModel):
    summary_text: str
    red_flags: Optional[List[RedFlag]] = []
    lab_results: Optional[dict] = None
    medications: Optional[List[dict]] = None


class SummaryCreate(SummaryBase):
    patient_id: UUID


class SummaryResponse(SummaryBase):
    id: UUID
    patient_id: UUID
    created_by: UUID
    version: int
    is_latest: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Patient with related data
class PatientDetail(PatientResponse):
    documents: List[DocumentResponse] = []
    summaries: List[SummaryResponse] = []


# Search and filter
class PatientSearch(BaseModel):
    query: Optional[str] = None
    gender: Optional[str] = None
    skip: int = 0
    limit: int = 20


# Error response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
