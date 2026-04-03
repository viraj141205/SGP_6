import api from './axios';

export const yieldApi = {
    predict: (data) => api.post('/api/yield/predict', data),
    getHistory: (params) => api.get('/api/yield/history', { params }),
    getRecord: (id) => api.get(`/api/yield/${id}`),
    deleteRecord: (id) => api.delete(`/api/yield/${id}`),
    getStats: () => api.get('/api/yield/stats'),
    getCrops: () => api.get('/api/yield/crops'),
    getRegions: () => api.get('/api/yield/regions'),
};
