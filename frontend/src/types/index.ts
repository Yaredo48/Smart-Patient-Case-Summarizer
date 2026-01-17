export interface User {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
    created_at: string;
}

export interface Patient {
    id: string;
    mrn: string;
    first_name: string;
    last_name: string;
    date_of_birth: string | null;
    gender: string | null;
    phone: string | null;
    email: string | null;
    created_at: string;
    updated_at: string | null;
}

export interface Document {
    id: string;
    patient_id: string;
    uploaded_by: string;
    file_name: string;
    file_type: string;
    file_size: number | null;
    processed: boolean;
    processing_status: string;
    error_message: string | null;
    created_at: string;
}

export interface Red Flag {
    category: string;
    finding: string;
    severity: string;
    value ?: string;
}

export interface Summary {
    id: string;
    patient_id: string;
    created_by: string;
    summary_text: string;
    red_flags: RedFlag[];
    lab_results: Record<string, any> | null;
    medications: Array<{ name: string; dosage: string }> | null;
    version: number;
    is_latest: boolean;
    created_at: string;
}

export interface PatientDetail extends Patient {
    documents: Document[];
    summaries: Summary[];
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name?: string;
    role?: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}
