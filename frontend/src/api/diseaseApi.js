import api from './axios';

export const diseaseApi = {
    detect: (formData) =>
        api.post('/api/disease/detect', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 60000,
        }),
    getHistory: (params) => api.get('/api/disease/history', { params }),
    getRecord: (id) => api.get(`/api/disease/${id}`),
    deleteRecord: (id) => api.delete(`/api/disease/${id}`),
    getStats: () => api.get('/api/disease/stats'),
};
