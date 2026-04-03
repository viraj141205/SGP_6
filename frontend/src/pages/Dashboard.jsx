import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Leaf, TrendingUp, Activity, Award, Zap, Clock } from 'lucide-react';
import { dashboardApi } from '../api/dashboardApi';
import StatCard from '../components/shared/StatCard';
import DiseaseDonutChart from '../components/charts/DiseaseDonutChart';
import YieldLineChart from '../components/charts/YieldLineChart';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import { useAuth } from '../context/AuthContext';
import { getGreeting, timeAgo } from '../utils/helpers';
import toast from 'react-hot-toast';

export default function Dashboard() {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [recent, setRecent] = useState([]);
    const [diseaseChart, setDiseaseChart] = useState([]);
    const [yieldChart, setYieldChart] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [s, r, dc, yc] = await Promise.all([
                    dashboardApi.getStats(),
                    dashboardApi.getRecentActivity(),
                    dashboardApi.getDiseaseChart(),
                    dashboardApi.getYieldChart(),
                ]);
                setStats(s.data);
                setRecent(r.data.recent_activity || []);
                setDiseaseChart(dc.data.chart_data || []);
                setYieldChart(yc.data.chart_data || []);
            } catch {
                toast.error('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) return <div className="h-64 flex items-center justify-center"><LoadingSpinner size="lg" text="Loading dashboard..." /></div>;

    return (
        <div>
            {/* Header */}
            <div className="page-header">
                <h1 className="text-3xl font-bold text-gray-900">
                    {getGreeting()}, {user?.full_name?.split(' ')[0]}! 🌱
                </h1>
                <p className="text-gray-500 mt-1">Here's your farm intelligence overview</p>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {[
                    { icon: <Activity size={22} />, label: 'Total Detections', value: stats?.total_detections || 0, color: 'green' },
                    { icon: <Leaf size={22} />, label: 'Diseases Found', value: stats?.diseases_found || 0, color: 'red' },
                    { icon: <TrendingUp size={22} />, label: 'Yield Predictions', value: stats?.total_yield_predictions || 0, color: 'blue' },
                    { icon: <Award size={22} />, label: 'Avg. Confidence', value: `${stats?.avg_confidence || 0}%`, color: 'amber' },
                ].map((s, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                        <StatCard {...s} />
                    </motion.div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid lg:grid-cols-5 gap-6 mb-8">
                <div className="card p-6 lg:col-span-3">
                    <h3 className="font-bold text-gray-900 mb-1">Disease Distribution</h3>
                    <p className="text-xs text-gray-500 mb-4">Your detected diseases breakdown</p>
                    <DiseaseDonutChart data={diseaseChart} />
                </div>
                <div className="card p-6 lg:col-span-2">
                    <h3 className="font-bold text-gray-900 mb-1">Yield Trend</h3>
                    <p className="text-xs text-gray-500 mb-4">Predicted yields over time</p>
                    <YieldLineChart data={yieldChart} />
                </div>
            </div>

            {/* Recent Activity + Quick Actions */}
            <div className="grid lg:grid-cols-3 gap-6">
                <div className="card p-6 lg:col-span-2">
                    <h3 className="font-bold text-gray-900 mb-4">Recent Activity</h3>
                    {recent.length === 0 ? (
                        <div className="text-center py-8 text-gray-400">
                            <Clock size={32} className="mx-auto mb-2" />
                            <p className="text-sm">No activity yet. Start by detecting a disease!</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recent.map((item, i) => (
                                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors">
                                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${item.type === 'disease' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'}`}>
                                        {item.type === 'disease' ? <Leaf size={18} /> : <TrendingUp size={18} />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-semibold text-gray-900 truncate">{item.crop}</p>
                                        <p className="text-xs text-gray-500 truncate">{item.result}</p>
                                    </div>
                                    <span className="text-xs text-gray-400 flex-shrink-0">{timeAgo(item.created_at)}</span>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="space-y-4">
                    <Link to="/detect">
                        <motion.div whileHover={{ scale: 1.03 }} className="card p-6 hover:shadow-lg transition-all cursor-pointer border-2 border-green-100 hover:border-green-300">
                            <div className="w-12 h-12 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mb-3">
                                <Leaf size={24} />
                            </div>
                            <h3 className="font-bold text-gray-900">Detect Disease</h3>
                            <p className="text-xs text-gray-500 mt-1">Upload a leaf photo for instant diagnosis</p>
                        </motion.div>
                    </Link>
                    <Link to="/yield">
                        <motion.div whileHover={{ scale: 1.03 }} className="card p-6 hover:shadow-lg transition-all cursor-pointer border-2 border-blue-100 hover:border-blue-300">
                            <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-3">
                                <TrendingUp size={24} />
                            </div>
                            <h3 className="font-bold text-gray-900">Predict Yield</h3>
                            <p className="text-xs text-gray-500 mt-1">Get accurate yield forecasts for your farm</p>
                        </motion.div>
                    </Link>
                </div>
            </div>
        </div>
    );
}
