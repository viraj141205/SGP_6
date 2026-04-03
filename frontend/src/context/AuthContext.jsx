import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/authApi';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const savedToken = localStorage.getItem('agrovision_token');
        const savedUser = localStorage.getItem('agrovision_user');
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
        setLoading(false);
    }, []);

    const login = useCallback(async (email, password) => {
        const res = await authApi.login({ email, password });
        const { access_token, user: userData } = res.data;
        localStorage.setItem('agrovision_token', access_token);
        localStorage.setItem('agrovision_user', JSON.stringify(userData));
        setToken(access_token);
        setUser(userData);
        return userData;
    }, []);

    const register = useCallback(async (email, password, full_name) => {
        const res = await authApi.register({ email, password, full_name });
        const { access_token, user: userData } = res.data;
        localStorage.setItem('agrovision_token', access_token);
        localStorage.setItem('agrovision_user', JSON.stringify(userData));
        setToken(access_token);
        setUser(userData);
        return userData;
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('agrovision_token');
        localStorage.removeItem('agrovision_user');
        setToken(null);
        setUser(null);
    }, []);

    const updateUser = useCallback((newData) => {
        const updated = { ...user, ...newData };
        setUser(updated);
        localStorage.setItem('agrovision_user', JSON.stringify(updated));
    }, [user]);

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}
