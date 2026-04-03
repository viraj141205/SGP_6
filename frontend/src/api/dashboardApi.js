import api from './axios';

export const dashboardApi = {
    getStats: () => api.get('/api/dashboard/stats'),
    getRecentActivity: () => api.get('/api/dashboard/recent'),
    getDiseaseChart: () => api.get('/api/dashboard/charts/disease'),
    getYieldChart: () => api.get('/api/dashboard/charts/yield'),
};
