import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Button,
    Paper,
    Grid,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Alert,
    List,
    ListItem,
    ListItemText,
    Divider,
    IconButton,
} from '@mui/material';
import { ArrowBack, Upload, AutoAwesome, CloudUpload, Delete } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { apiClient } from '../services/api';
import { PatientDetail, Document, Summary } from '../types';

const PatientDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [patient, setPatient] = useState<PatientDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [uploading, setUploading] = useState(false);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        if (id) {
            loadPatientData();
        }
    }, [id]);

    const loadPatientData = async () => {
        try {
            setLoading(true);
            const data = await apiClient.getPatient(id!);
            setPatient(data);
        } catch (err: any) {
            setError('Failed to load patient');
        } finally {
            setLoading(false);
        }
    };

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (!id) return;

        setUploading(true);
        try {
            for (const file of acceptedFiles) {
                await apiClient.uploadDocument(id, file);
            }
            await loadPatientData(); // Reload to show new documents
            setError('');
        } catch (err: any) {
            setError('Failed to upload documents');
        } finally {
            setUploading(false);
        }
    }, [id]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'image/*': ['.png', '.jpg', '.jpeg', '.tiff'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        },
    });

    const handleGenerateSummary = async () => {
        if (!id) return;

        setGenerating(true);
        try {
            await apiClient.generateSummary(id);
            setError('');
            alert('Summary generation started! Please wait...');
            // Poll for summary updates
            setTimeout(() => loadPatientData(), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to generate summary');
        } finally {
            setGenerating(false);
        }
    };

    const handleDeleteDocument = async (docId: string) => {
        if (window.confirm('Delete this document?')) {
            try {
                await apiClient.deleteDocument(docId);
                await loadPatientData();
            } catch (err) {
                setError('Failed to delete document');
            }
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (!patient) {
        return (
            <Container>
                <Alert severity="error">Patient not found</Alert>
            </Container>
        );
    }

    const latestSummary = patient.summaries?.find(s => s.is_latest);

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
                Back
            </Button>

            {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

            {/* Patient Info */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" gutterBottom>
                    {patient.first_name} {patient.last_name}
                </Typography>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Typography color="text.secondary">MRN</Typography>
                        <Typography variant="body1">{patient.mrn}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Typography color="text.secondary">Date of Birth</Typography>
                        <Typography variant="body1">
                            {patient.date_of_birth
                                ? new Date(patient.date_of_birth).toLocaleDateString()
                                : 'N/A'}
                        </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Typography color="text.secondary">Gender</Typography>
                        <Typography variant="body1">{patient.gender || 'N/A'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Typography color="text.secondary">Contact</Typography>
                        <Typography variant="body1">{patient.phone || patient.email || 'N/A'}</Typography>
                    </Grid>
                </Grid>
            </Paper>

            <Grid container spacing={3}>
                {/* Documents Section */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="h6">Documents</Typography>
                                <Chip
                                    label={`${patient.documents?.length || 0} files`}
                                    color="primary"
                                    size="small"
                                />
                            </Box>

                            {/* Upload Zone */}
                            <Box
                                {...getRootProps()}
                                sx={{
                                    border: '2px dashed',
                                    borderColor: isDragActive ? 'primary.main' : 'divider',
                                    borderRadius: 2,
                                    p: 3,
                                    textAlign: 'center',
                                    cursor: 'pointer',
                                    bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                                    mb: 2,
                                }}
                            >
                                <input {...getInputProps()} />
                                <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                                <Typography variant="body1">
                                    {uploading ? 'Uploading...' : 'Drag & drop files or click to browse'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    PDF, Images, Word documents
                                </Typography>
                            </Box>

                            {/* Document List */}
                            <List>
                                {patient.documents?.map((doc: Document) => (
                                    <React.Fragment key={doc.id}>
                                        <ListItem
                                            secondaryAction={
                                                <IconButton edge="end" onClick={() => handleDeleteDocument(doc.id)}>
                                                    <Delete />
                                                </IconButton>
                                            }
                                        >
                                            <ListItemText
                                                primary={doc.file_name}
                                                secondary={
                                                    <>
                                                        <Chip
                                                            label={doc.processing_status}
                                                            size="small"
                                                            color={doc.processed ? 'success' : 'default'}
                                                            sx={{ mr: 1 }}
                                                        />
                                                        {new Date(doc.created_at).toLocaleString()}
                                                    </>
                                                }
                                            />
                                        </ListItem>
                                        <Divider />
                                    </React.Fragment>
                                ))}
                                {!patient.documents?.length && (
                                    <ListItem>
                                        <ListItemText secondary="No documents uploaded" />
                                    </ListItem>
                                )}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Summary Section */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="h6">AI Summary</Typography>
                                <Button
                                    startIcon={generating ? <CircularProgress size={20} /> : <AutoAwesome />}
                                    variant="contained"
                                    onClick={handleGenerateSummary}
                                    disabled={generating || !patient.documents?.some(d => d.processed)}
                                >
                                    {generating ? 'Generating...' : 'Generate'}
                                </Button>
                            </Box>

                            {latestSummary ? (
                                <Box>
                                    {/* Red Flags */}
                                    {latestSummary.red_flags && latestSummary.red_flags.length > 0 && (
                                        <Box sx={{ mb: 2 }}>
                                            <Typography variant="subtitle2" color="error" gutterBottom>
                                                🔴 Red Flags
                                            </Typography>
                                            {latestSummary.red_flags.map((flag, idx) => (
                                                <Alert key={idx} severity="error" sx={{ mb: 1 }}>
                                                    <strong>{flag.category}:</strong> {flag.finding}
                                                </Alert>
                                            ))}
                                        </Box>
                                    )}

                                    {/* Summary Text */}
                                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                                        <Typography
                                            variant="body2"
                                            component="pre"
                                            sx={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}
                                        >
                                            {latestSummary.summary_text}
                                        </Typography>
                                    </Paper>

                                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                        Generated: {new Date(latestSummary.created_at).toLocaleString()}
                                    </Typography>
                                </Box>
                            ) : (
                                <Alert severity="info">
                                    No summary available. Upload documents and click "Generate" to create a summary.
                                </Alert>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
};

export default PatientDetailPage;
