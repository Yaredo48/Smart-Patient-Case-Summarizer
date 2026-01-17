import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginCredentials, RegisterData, AuthResponse } from '../types';
import { apiClient } from '../services/api';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in on mount
        const loadUser = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    const currentUser = await apiClient.getCurrentUser();
                    setUser(currentUser);
                } catch (error) {
                    // Token is invalid, clear it
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user');
                }
            }
            setIsLoading(false);
        };

        loadUser();
    }, []);

    const login = async (credentials: LoginCredentials) => {
        const response: AuthResponse = await apiClient.login(credentials);
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        setUser(response.user);
    };

    const register = async (data: RegisterData) => {
        const newUser = await apiClient.register(data);
        // After registration, log in
        await login({ email: data.email, password: data.password });
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setUser(null);
    };

    const value = {
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
