import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
    Container,
    Box,
    Paper,
    TextField,
    Button,
    Typography,
    Alert,
    Link,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await register({
                email,
                password,
                full_name: fullName,
                role: 'doctor',
            });
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box
                sx={{
                    minHeight: '100vh',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
                    <Typography variant="h4" component="h1" gutterBottom align="center">
                        Create Account
                    </Typography>
                    <Typography variant="body1" gutterBottom align="center" color="text.secondary">
                        Join Smart Patient Case Summarizer
                    </Typography>

                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                        <TextField
                            fullWidth
                            label="Full Name"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            margin="normal"
                            autoFocus
                        />
                        <TextField
                            fullWidth
                            label="Email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            margin="normal"
                            autoComplete="email"
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            margin="normal"
                            autoComplete="new-password"
                            helperText="Minimum 8 characters"
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            size="large"
                            disabled={isLoading}
                            sx={{ mt: 3, mb: 2 }}
                        >
                            {isLoading ? 'Creating account...' : 'Register'}
                        </Button>

                        <Box sx={{ textAlign: 'center' }}>
                            <Link component={RouterLink} to="/login" variant="body2">
                                Already have an account? Login here
                            </Link>
                        </Box>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default RegisterPage;
