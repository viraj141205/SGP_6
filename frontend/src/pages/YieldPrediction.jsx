import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, TrendingUp, CheckCircle, Zap } from 'lucide-react';
import { yieldApi } from '../api/yieldApi';
import ComparisonBarChart from '../components/charts/ComparisonBarChart';
import { CROPS, SEASONS, SOIL_TYPES, INDIAN_STATES } from '../utils/constants';
import { formatYield, getPerformanceColor } from '../utils/helpers';
import toast from 'react-hot-toast';

const DEFAULT_FORM = {
    crop_type: 'Wheat', region: 'Punjab', season: 'Rabi', area_acres: 2,
    soil_type: 'Loam', soil_ph: 6.5, nitrogen: 80, phosphorus: 50, potassium: 50,
    rainfall: 700, temperature: 22, humidity: 65
};

function Step1({ data, onChange, onNext }) {
    return (
        <div className="space-y-5">
            <h2 className="text-xl font-bold text-gray-900">Step 1 — Crop & Location</h2>
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="label">Crop Type</label>
                    <select value={data.crop_type} onChange={e => onChange('crop_type', e.target.value)} className="input-field">
                        {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
                <div>
                    <label className="label">Region / State</label>
                    <select value={data.region} onChange={e => onChange('region', e.target.value)} className="input-field">
                        {INDIAN_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div>
                    <label className="label">Season</label>
                    <select value={data.season} onChange={e => onChange('season', e.target.value)} className="input-field">
                        {SEASONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div>
                    <label className="label">Farm Area (Acres)</label>
                    <input type="number" min="0.1" step="0.1" value={data.area_acres}
                        onChange={e => onChange('area_acres', parseFloat(e.target.value) || 1)}
                        className="input-field" placeholder="e.g. 2.5" />
                </div>
            </div>
            <button onClick={onNext} className="btn-primary ml-auto">Next <ChevronRight size={18} /></button>
        </div>
    );
}

function NpkBadge({ value, type }) {
    const optimal = { nitrogen: [40, 100], phosphorus: [25, 80], potassium: [30, 100] };
    const [lo, hi] = optimal[type] || [0, 100];
    if (value < lo) return <span className="badge badge-red text-xs ml-2">Low</span>;
    if (value > hi) return <span className="badge badge-amber text-xs ml-2">High</span>;
    return <span className="badge badge-green text-xs ml-2">Optimal</span>;
}

function Step2({ data, onChange, onNext, onBack }) {
    return (
        <div className="space-y-5">
            <h2 className="text-xl font-bold text-gray-900">Step 2 — Soil & Weather</h2>
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="label">Soil Type</label>
                    <select value={data.soil_type} onChange={e => onChange('soil_type', e.target.value)} className="input-field">
                        {SOIL_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div>
                    <label className="label">Soil pH — {data.soil_ph}</label>
                    <input type="range" min="3" max="10" step="0.1" value={data.soil_ph}
                        onChange={e => onChange('soil_ph', parseFloat(e.target.value))} className="w-full accent-green-600" />
                    <div className="flex justify-between text-xs text-gray-400 mt-1"><span>3 (Acidic)</span><span>7 (Neutral)</span><span>10 (Alkaline)</span></div>
                </div>
                {['nitrogen', 'phosphorus', 'potassium'].map(field => (
                    <div key={field}>
                        <label className="label capitalize">{field} (N/P/K) kg/ha <NpkBadge value={data[field]} type={field} /></label>
                        <input type="number" min="0" max="200" value={data[field]}
                            onChange={e => onChange(field, parseFloat(e.target.value) || 0)} className="input-field" />
                    </div>
                ))}
                <div>
                    <label className="label">Annual Rainfall (mm) — {data.rainfall}</label>
                    <input type="range" min="50" max="3000" step="10" value={data.rainfall}
                        onChange={e => onChange('rainfall', parseInt(e.target.value))} className="w-full accent-green-600" />
                </div>
                <div>
                    <label className="label">Temperature (°C) — {data.temperature}°C</label>
                    <input type="range" min="-10" max="50" step="0.5" value={data.temperature}
                        onChange={e => onChange('temperature', parseFloat(e.target.value))} className="w-full accent-green-600" />
                </div>
                <div>
                    <label className="label">Humidity (%) — {data.humidity}%</label>
                    <input type="range" min="10" max="100" step="1" value={data.humidity}
                        onChange={e => onChange('humidity', parseInt(e.target.value))} className="w-full accent-green-600" />
                </div>
            </div>
            <div className="flex gap-3">
                <button onClick={onBack} className="btn-secondary"><ChevronLeft size={18} /> Back</button>
                <button onClick={onNext} className="btn-primary ml-auto">Review <ChevronRight size={18} /></button>
            </div>
        </div>
    );
}

function Step3({ data, onBack, onSubmit, loading }) {
    const rows = [
        ['Crop', data.crop_type], ['Region', data.region], ['Season', data.season],
        ['Area', `${data.area_acres} acres`], ['Soil Type', data.soil_type], ['Soil pH', data.soil_ph],
        ['Nitrogen', `${data.nitrogen} kg/ha`], ['Phosphorus', `${data.phosphorus} kg/ha`],
        ['Potassium', `${data.potassium} kg/ha`], ['Rainfall', `${data.rainfall} mm`],
        ['Temperature', `${data.temperature}°C`], ['Humidity', `${data.humidity}%`]
    ];
    return (
        <div className="space-y-5">
            <h2 className="text-xl font-bold text-gray-900">Step 3 — Review & Predict</h2>
            <div className="card bg-green-50 border border-green-100 p-5">
                <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                    {rows.map(([k, v]) => (
                        <div key={k} className="flex justify-between text-sm border-b border-green-100 pb-2">
                            <span className="text-gray-600 font-medium">{k}</span>
                            <span className="text-gray-900 font-semibold">{v}</span>
                        </div>
                    ))}
                </div>
            </div>
            <div className="flex gap-3">
                <button onClick={onBack} className="btn-secondary"><ChevronLeft size={18} /> Back</button>
                <button onClick={onSubmit} disabled={loading} className="btn-primary flex-1 justify-center py-3.5 text-base">
                    {loading ? <><div className="w-5 h-5 spinner border-white border-t-transparent" /> Predicting...</> : <><TrendingUp size={20} /> Predict Yield</>}
                </button>
            </div>
        </div>
    );
}

function YieldResult({ result, onNewPrediction }) {
    return (
        <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}
            className="space-y-4">
            {result.is_demo_mode && (
                <div className="demo-banner"><Zap size={16} className="flex-shrink-0" />
                    <span><strong>Demo Mode:</strong> Train models on real data for accurate predictions.</span></div>
            )}

            {/* Main Result */}
            <div className="card p-6 text-center">
                <p className="text-sm text-gray-500 mb-1">Predicted Yield</p>
                <p className="text-5xl font-black" style={{ color: getPerformanceColor(result.performance_rating) }}>
                    {formatYield(result.predicted_yield)}
                </p>
                <p className="text-gray-500 text-sm mt-1">{result.yield_unit}</p>
                <div className="flex items-center justify-center gap-2 mt-3">
                    <span className="badge" style={{
                        backgroundColor: `${getPerformanceColor(result.performance_rating)}20`,
                        color: getPerformanceColor(result.performance_rating)
                    }}>{result.performance_rating}</span>
                    <span className="text-sm text-gray-600">{result.yield_comparison}</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                    Range: {formatYield(result.confidence_lower)} — {formatYield(result.confidence_upper)} {result.yield_unit}
                </p>
            </div>

            {/* Comparison Chart */}
            <div className="card p-5">
                <h3 className="font-semibold text-gray-900 mb-3 text-sm">Yield Comparison</h3>
                <ComparisonBarChart
                    predicted={result.predicted_yield}
                    average={result.avg_yield_for_crop}
                    best={result.confidence_upper * 1.1}
                />
            </div>

            {/* Recommendations */}
            <div className="card p-5">
                <h3 className="font-semibold text-gray-900 mb-3">Recommendations</h3>
                <ol className="space-y-3">
                    {result.recommendations?.map((r, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm">
                            <span className="w-5 h-5 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                            <span className="text-gray-600 leading-relaxed">{r}</span>
                        </li>
                    ))}
                </ol>
            </div>

            <p className="text-xs text-gray-400 text-center">Model: {result.model_used}</p>
            <button onClick={onNewPrediction} className="btn-secondary w-full justify-center">New Prediction</button>
        </motion.div>
    );
}

export default function YieldPrediction() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState(DEFAULT_FORM);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const onChange = (k, v) => setFormData(prev => ({ ...prev, [k]: v }));

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const res = await yieldApi.predict(formData);
            setResult(res.data);
            toast.success('Yield prediction complete!');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Prediction failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => { setResult(null); setStep(1); setFormData(DEFAULT_FORM); };

    const stepLabels = ['Crop & Location', 'Soil & Weather', 'Review & Predict'];

    return (
        <div>
            <div className="page-header">
                <h1 className="section-title">Yield Prediction</h1>
                <p className="section-subtitle">Enter your farm parameters to predict crop yield accurately</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Form Column */}
                <div className="card p-6">
                    {!result ? (
                        <>
                            {/* Progress Bar */}
                            <div className="mb-6">
                                <div className="flex items-center gap-2 mb-3">
                                    {stepLabels.map((label, i) => (
                                        <div key={i} className="flex items-center gap-2 flex-1">
                                            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${step > i + 1 ? 'bg-green-600 text-white' : step === i + 1 ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                                                {step > i + 1 ? <CheckCircle size={14} /> : i + 1}
                                            </div>
                                            <span className={`text-xs hidden sm:block ${step >= i + 1 ? 'text-green-700 font-medium' : 'text-gray-400'}`}>{label}</span>
                                            {i < 2 && <div className={`flex-1 h-0.5 ${step > i + 1 ? 'bg-green-600' : 'bg-gray-200'}`} />}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <AnimatePresence mode="wait">
                                <motion.div key={step} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.25 }}>
                                    {step === 1 && <Step1 data={formData} onChange={onChange} onNext={() => setStep(2)} />}
                                    {step === 2 && <Step2 data={formData} onChange={onChange} onNext={() => setStep(3)} onBack={() => setStep(1)} />}
                                    {step === 3 && <Step3 data={formData} onBack={() => setStep(2)} onSubmit={handleSubmit} loading={loading} />}
                                </motion.div>
                            </AnimatePresence>
                        </>
                    ) : (
                        <YieldResult result={result} onNewPrediction={handleReset} />
                    )}
                </div>

                {/* Info Column */}
                <div className="space-y-4">
                    <div className="card p-5">
                        <h3 className="font-bold text-gray-900 mb-3">About the Ensemble Model</h3>
                        {[
                            { label: 'XGBoost', weight: '45%', color: '#16a34a' },
                            { label: 'Deep Neural Network', weight: '35%', color: '#3b82f6' },
                            { label: 'Random Forest', weight: '20%', color: '#f59e0b' },
                        ].map(m => (
                            <div key={m.label} className="flex items-center gap-3 mb-3">
                                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: m.color }}>
                                    {m.weight}
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-gray-900">{m.label}</p>
                                    <p className="text-xs text-gray-500">Weight: {m.weight}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="card p-5 bg-amber-50 border border-amber-100">
                        <h4 className="font-bold text-amber-900 mb-2">💡 Tips for accuracy</h4>
                        <ul className="space-y-1.5 text-xs text-amber-800">
                            {['Use soil test results for N, P, K values', 'Use 30-year average rainfall for your region', 'Select the correct season for your crop', 'Include accurate farm area for total yield estimation'].map(t => (
                                <li key={t} className="flex items-start gap-1.5"><span>•</span>{t}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
