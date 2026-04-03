import api from './axios';

export const authApi = {
    register: (data) => api.post('/api/auth/register', data),
    login: (data) => api.post('/api/auth/login', data),
    getMe: () => api.get('/api/auth/me'),
    updateMe: (data) => api.put('/api/auth/me', data),
    changePassword: (data) => api.put('/api/auth/me/password', data),
    deleteAccount: () => api.delete('/api/auth/me'),
};
