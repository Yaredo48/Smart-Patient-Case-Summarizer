import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box, CircularProgress } from '@mui/material';
import { useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import PatientDetailPage from './pages/PatientDetailPage';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth();

    return (
        <>
            {isAuthenticated && (
                <AppBar position="sticky">
                    <Toolbar>
                        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                            Patient Summarizer
                        </Typography>
                        <Typography variant="body1" sx={{ mr: 2 }}>
                            {user?.full_name || user?.email}
                        </Typography>
                        <Button color="inherit" onClick={logout}>
                            Logout
                        </Button>
                    </Toolbar>
                </AppBar>
            )}

            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route
                    path="/"
                    element={
                        <PrivateRoute>
                            <DashboardPage />
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/patients/:id"
                    element={
                        <PrivateRoute>
                            <PatientDetailPage />
                        </PrivateRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </>
    );
};

export default App;
