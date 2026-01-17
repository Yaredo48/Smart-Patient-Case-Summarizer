import axios, { AxiosInstance, AxiosError } from 'axios';
import { AuthResponse, LoginCredentials, RegisterData, User, Patient, PatientDetail, Document, Summary } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: `${API_BASE_URL}/api`,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Add request interceptor to attach auth token
        this.client.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('access_token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error: AxiosError) => {
                if (error.response?.status === 401) {
                    // Clear auth and redirect to login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    // Auth endpoints
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new FormData();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        const response = await this.client.post<AuthResponse>('/auth/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    async register(data: RegisterData): Promise<User> {
        const response = await this.client.post<User>('/auth/register', data);
        return response.data;
    }

    async getCurrentUser(): Promise<User> {
        const response = await this.client.get<User>('/auth/me');
        return response.data;
    }

    // Patient endpoints
    async getPatients(params?: { skip?: number; limit?: number; search?: string }): Promise<Patient[]> {
        const response = await this.client.get<Patient[]>('/patients/', { params });
        return response.data;
    }

    async getPatient(id: string): Promise<PatientDetail> {
        const response = await this.client.get<PatientDetail>(`/patients/${id}`);
        return response.data;
    }

    async createPatient(data: Omit<Patient, 'id' | 'created_at' | 'updated_at'>): Promise<Patient> {
        const response = await this.client.post<Patient>('/patients/', data);
        return response.data;
    }

    async updatePatient(id: string, data: Partial<Patient>): Promise<Patient> {
        const response = await this.client.put<Patient>(`/patients/${id}`, data);
        return response.data;
    }

    async deletePatient(id: string): Promise<void> {
        await this.client.delete(`/patients/${id}`);
    }

    // Document endpoints
    async uploadDocument(patientId: string, file: File): Promise<Document> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.client.post<Document>(
            `/documents/upload/${patientId}`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        return response.data;
    }

    async getPatientDocuments(patientId: string): Promise<Document[]> {
        const response = await this.client.get<Document[]>(`/documents/patient/${patientId}`);
        return response.data;
    }

    async getDocument(id: string): Promise<Document> {
        const response = await this.client.get<Document>(`/documents/${id}`);
        return response.data;
    }

    async deleteDocument(id: string): Promise<void> {
        await this.client.delete(`/documents/${id}`);
    }

    // Summary endpoints
    async generateSummary(patientId: string): Promise<{ message: string; patient_id: string }> {
        const response = await this.client.post(`/summaries/generate/${patientId}`);
        return response.data;
    }

    async getPatientSummaries(patientId: string, latestOnly = true): Promise<Summary[]> {
        const response = await this.client.get<Summary[]>(`/summaries/patient/${patientId}`, {
            params: { latest_only: latestOnly },
        });
        return response.data;
    }

    async getSummary(id: string): Promise<Summary> {
        const response = await this.client.get<Summary>(`/summaries/${id}`);
        return response.data;
    }

    async deleteSummary(id: string): Promise<void> {
        await this.client.delete(`/summaries/${id}`);
    }
}

export const apiClient = new ApiClient();
