import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Button,
    TextField,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Alert,
} from '@mui/material';
import { Add, Visibility, Delete, Search } from '@mui/icons-material';
import { apiClient } from '../services/api';
import { Patient } from '../types';

const DashboardPage: React.FC = () => {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [newPatient, setNewPatient] = useState({
        mrn: '',
        first_name: '',
        last_name: '',
        date_of_birth: '',
        gender: '',
        phone: '',
        email: '',
    });
    const [error, setError] = useState('');

    const navigate = useNavigate();

    useEffect(() => {
        loadPatients();
    }, [searchQuery]);

    const loadPatients = async () => {
        try {
            setLoading(true);
            const data = await apiClient.getPatients({ search: searchQuery || undefined });
            setPatients(data);
        } catch (err: any) {
            setError('Failed to load patients');
        } finally {
            setLoading(false);
        }
    };

    const handleCreatePatient = async () => {
        try {
            const created = await apiClient.createPatient(newPatient as any);
            setPatients([created, ...patients]);
            setOpenDialog(false);
            setNewPatient({
                mrn: '',
                first_name: '',
                last_name: '',
                date_of_birth: '',
                gender: '',
                phone: '',
                email: '',
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create patient');
        }
    };

    const handleDeletePatient = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this patient?')) {
            try {
                await apiClient.deletePatient(id);
                setPatients(patients.filter(p => p.id !== id));
            } catch (err: any) {
                setError('Failed to delete patient');
            }
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Patient Dashboard
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setOpenDialog(true)}
                >
                    New Patient
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

            <Box sx={{ mb: 3 }}>
                <TextField
                    fullWidth
                    placeholder="Search by name or MRN..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                        startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                />
            </Box>

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>MRN</TableCell>
                                <TableCell>Name</TableCell>
                                <TableCell>Date of Birth</TableCell>
                                <TableCell>Gender</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {patients.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} align="center">
                                        <Typography color="text.secondary">No patients found</Typography>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                patients.map((patient) => (
                                    <TableRow key={patient.id} hover>
                                        <TableCell>{patient.mrn}</TableCell>
                                        <TableCell>{`${patient.first_name} ${patient.last_name}`}</TableCell>
                                        <TableCell>
                                            {patient.date_of_birth
                                                ? new Date(patient.date_of_birth).toLocaleDateString()
                                                : '-'}
                                        </TableCell>
                                        <TableCell>{patient.gender || '-'}</TableCell>
                                        <TableCell>
                                            <IconButton
                                                color="primary"
                                                onClick={() => navigate(`/patients/${patient.id}`)}
                                                title="View Details"
                                            >
                                                <Visibility />
                                            </IconButton>
                                            <IconButton
                                                color="error"
                                                onClick={() => handleDeletePatient(patient.id)}
                                                title="Delete"
                                            >
                                                <Delete />
                                            </IconButton>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}

            {/* Create Patient Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Create New Patient</DialogTitle>
                <DialogContent>
                    <TextField
                        fullWidth
                        label="MRN"
                        value={newPatient.mrn}
                        onChange={(e) => setNewPatient({ ...newPatient, mrn: e.target.value })}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="First Name"
                        value={newPatient.first_name}
                        onChange={(e) => setNewPatient({ ...newPatient, first_name: e.target.value })}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="Last Name"
                        value={newPatient.last_name}
                        onChange={(e) => setNewPatient({ ...newPatient, last_name: e.target.value })}
                        margin="normal"
                        required
                    />
                    <TextField
                        fullWidth
                        label="Date of Birth"
                        type="date"
                        value={newPatient.date_of_birth}
                        onChange={(e) => setNewPatient({ ...newPatient, date_of_birth: e.target.value })}
                        margin="normal"
                        InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                        fullWidth
                        label="Gender"
                        value={newPatient.gender}
                        onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Phone"
                        value={newPatient.phone}
                        onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })}
                        margin="normal"
                    />
                    <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        value={newPatient.email}
                        onChange={(e) => setNewPatient({ ...newPatient, email: e.target.value })}
                        margin="normal"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
                    <Button onClick={handleCreatePatient} variant="contained">
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default DashboardPage;
