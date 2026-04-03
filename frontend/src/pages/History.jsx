import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Leaf, TrendingUp, Trash2, Eye, ChevronLeft, ChevronRight } from 'lucide-react';
import { diseaseApi } from '../api/diseaseApi';
import { yieldApi } from '../api/yieldApi';
import EmptyState from '../components/shared/EmptyState';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import { timeAgo, formatYield, truncate, getSeverityClass } from '../utils/helpers';
import toast from 'react-hot-toast';

function TabButton({ active, onClick, icon, label, count }) {
    return (
        <button onClick={onClick}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${active ? 'bg-green-600 text-white shadow-sm' : 'bg-white text-gray-600 hover:bg-green-50'}`}>
            {icon}
            <span>{label}</span>
            {count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${active ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'}`}>
                    {count}
                </span>
            )}
        </button>
    );
}

function DiseaseRow({ item, onDelete }) {
    return (
        <motion.tr initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="hover:bg-gray-50 transition-colors">
            <td className="py-3.5 px-5">
                {item.image_url ? (
                    <img src={item.image_url} alt="" className="w-10 h-10 rounded-lg object-cover" />
                ) : (
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <Leaf size={16} className="text-green-600" />
                    </div>
                )}
            </td>
            <td className="py-3.5 px-3">
                <p className="font-semibold text-gray-900 text-sm">{item.disease_name}</p>
                <p className="text-xs text-gray-500">{item.crop_type}</p>
            </td>
            <td className="py-3.5 px-3">
                <span className={`badge ${getSeverityClass(item.severity)}`}>{item.severity}</span>
            </td>
            <td className="py-3.5 px-3 text-sm text-gray-600">{Math.round(item.confidence * 100)}%</td>
            <td className="py-3.5 px-3 text-xs text-gray-500">{timeAgo(item.created_at)}</td>
            <td className="py-3.5 px-3">
                <button onClick={() => onDelete(item.id)}
                    className="w-8 h-8 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg flex items-center justify-center transition-colors">
                    <Trash2 size={15} />
                </button>
            </td>
        </motion.tr>
    );
}

function YieldRow({ item, onDelete }) {
    return (
        <motion.tr initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="hover:bg-gray-50 transition-colors">
            <td className="py-3.5 px-5">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <TrendingUp size={16} className="text-blue-600" />
                </div>
            </td>
            <td className="py-3.5 px-3">
                <p className="font-semibold text-gray-900 text-sm">{item.crop_type}</p>
                <p className="text-xs text-gray-500">{item.region} • {item.season}</p>
            </td>
            <td className="py-3.5 px-3">
                <p className="font-bold text-green-700">{formatYield(item.predicted_yield)}</p>
                <p className="text-xs text-gray-500">{item.yield_unit}</p>
            </td>
            <td className="py-3.5 px-3">
                <span className="badge badge-green">{item.performance_rating}</span>
            </td>
            <td className="py-3.5 px-3 text-xs text-gray-500">{timeAgo(item.created_at)}</td>
            <td className="py-3.5 px-3">
                <button onClick={() => onDelete(item.id)}
                    className="w-8 h-8 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg flex items-center justify-center transition-colors">
                    <Trash2 size={15} />
                </button>
            </td>
        </motion.tr>
    );
}

const PAGE_SIZE = 10;

export default function History() {
    const [tab, setTab] = useState('disease');
    const [diseaseHistory, setDiseaseHistory] = useState([]);
    const [yieldHistory, setYieldHistory] = useState([]);
    const [loadingD, setLoadingD] = useState(true);
    const [loadingY, setLoadingY] = useState(true);
    const [pageD, setPageD] = useState(1);
    const [pageY, setPageY] = useState(1);

    useEffect(() => {
        diseaseApi.getHistory({ page: pageD, limit: PAGE_SIZE }).then(r => {
            setDiseaseHistory(r.data.items || []);
        }).catch(() => toast.error('Failed to load disease history')).finally(() => setLoadingD(false));
    }, [pageD]);

    useEffect(() => {
        yieldApi.getHistory({ page: pageY, limit: PAGE_SIZE }).then(r => {
            setYieldHistory(r.data.items || []);
        }).catch(() => toast.error('Failed to load yield history')).finally(() => setLoadingY(false));
    }, [pageY]);

    const deleteDisease = async (id) => {
        try {
            await diseaseApi.deleteRecord(id);
            setDiseaseHistory(h => h.filter(r => r.id !== id));
            toast.success('Record deleted');
        } catch { toast.error('Failed to delete'); }
    };

    const deleteYield = async (id) => {
        try {
            await yieldApi.deleteRecord(id);
            setYieldHistory(h => h.filter(r => r.id !== id));
            toast.success('Record deleted');
        } catch { toast.error('Failed to delete'); }
    };

    return (
        <div>
            <div className="page-header">
                <h1 className="section-title">History</h1>
                <p className="section-subtitle">Your previous detections and predictions</p>
            </div>

            <div className="flex gap-2 mb-6">
                <TabButton active={tab === 'disease'} onClick={() => setTab('disease')}
                    icon={<Leaf size={16} />} label="Disease Detections" count={diseaseHistory.length} />
                <TabButton active={tab === 'yield'} onClick={() => setTab('yield')}
                    icon={<TrendingUp size={16} />} label="Yield Predictions" count={yieldHistory.length} />
            </div>

            {tab === 'disease' && (
                <div className="card overflow-hidden">
                    {loadingD ? (
                        <div className="p-12 flex justify-center"><LoadingSpinner text="Loading history..." /></div>
                    ) : diseaseHistory.length === 0 ? (
                        <EmptyState icon={<Leaf size={28} />} title="No detections yet"
                            description="Start by uploading a leaf image to detect diseases." />
                    ) : (
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    {['Image', 'Disease', 'Severity', 'Confidence', 'Date', ''].map(h => (
                                        <th key={h} className="py-3 px-3 text-left table-header text-xs">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {diseaseHistory.map(item => (
                                    <DiseaseRow key={item.id} item={item} onDelete={deleteDisease} />
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {tab === 'yield' && (
                <div className="card overflow-hidden">
                    {loadingY ? (
                        <div className="p-12 flex justify-center"><LoadingSpinner text="Loading history..." /></div>
                    ) : yieldHistory.length === 0 ? (
                        <EmptyState icon={<TrendingUp size={28} />} title="No predictions yet"
                            description="Start by entering your farm details to predict yield." />
                    ) : (
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-100">
                                <tr>
                                    {['', 'Crop & Region', 'Yield', 'Performance', 'Date', ''].map(h => (
                                        <th key={h} className="py-3 px-3 text-left table-header text-xs">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {yieldHistory.map(item => (
                                    <YieldRow key={item.id} item={item} onDelete={deleteYield} />
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}
