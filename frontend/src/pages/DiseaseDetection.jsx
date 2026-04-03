import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Leaf, X, CheckCircle, AlertTriangle, Info, ChevronDown, ChevronUp, Shield, Zap } from 'lucide-react';
import { diseaseApi } from '../api/diseaseApi';
import ConfidenceBar from '../components/shared/ConfidenceBar';
import { formatConfidence, fileSizeStr, getSeverityClass } from '../utils/helpers';
import toast from 'react-hot-toast';

function DiseaseResult({ result, onScanAnother }) {
    const [showTreatment, setShowTreatment] = useState(true);
    const [showPrevention, setShowPrevention] = useState(false);

    const severityColor = {
        None: 'text-green-600 bg-green-50', Low: 'text-green-600 bg-green-50',
        Medium: 'text-amber-700 bg-amber-50', High: 'text-red-700 bg-red-50'
    }[result.severity] || 'text-amber-700 bg-amber-50';

    return (
        <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}
            className="space-y-4">
            {result.is_demo_mode && (
                <div className="demo-banner">
                    <Zap size={16} className="flex-shrink-0" />
                    <span><strong>Demo Mode:</strong> Train the model for real predictions. Results are simulated.</span>
                </div>
            )}

            {/* Header */}
            <div className="card p-5">
                <div className="flex items-start justify-between mb-3">
                    <div>
                        <span className="badge badge-green text-xs mb-2">🌿 {result.crop_type}</span>
                        <h2 className="text-xl font-bold text-gray-900">{result.disease_name}</h2>
                    </div>
                    <div className={`px-3 py-1.5 rounded-full text-sm font-bold ${result.is_healthy ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {result.is_healthy ? '✓ Healthy' : '⚠ Diseased'}
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                        <p className="text-xs text-gray-500 mb-2">Confidence</p>
                        <ConfidenceBar value={result.confidence} showPercent />
                    </div>
                    <div>
                        <p className="text-xs text-gray-500 mb-2">Severity</p>
                        <span className={`badge ${getSeverityClass(result.severity)}`}>{result.severity}</span>
                    </div>
                </div>
            </div>

            {/* Description */}
            <div className="card p-5">
                <div className="flex items-center gap-2 mb-2">
                    <Info size={16} className="text-blue-500" />
                    <h3 className="font-semibold text-gray-900 text-sm">About this disease</h3>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">{result.description}</p>
                {result.symptoms?.length > 0 && (
                    <div className="mt-3">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Symptoms:</p>
                        <ul className="space-y-1">
                            {result.symptoms.map((s, i) => (
                                <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
                                    <span className="text-red-400 mt-0.5">•</span>{s}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Treatment */}
            <div className="card overflow-hidden">
                <button onClick={() => setShowTreatment(!showTreatment)}
                    className="w-full flex items-center justify-between p-5 text-left hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-red-100 text-red-600 rounded-lg flex items-center justify-center">
                            <AlertTriangle size={14} />
                        </div>
                        <span className="font-semibold text-gray-900">Treatment Plan</span>
                    </div>
                    {showTreatment ? <ChevronUp size={18} className="text-gray-400" /> : <ChevronDown size={18} className="text-gray-400" />}
                </button>
                <AnimatePresence>
                    {showTreatment && (
                        <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                            <ol className="px-5 pb-5 space-y-2">
                                {result.treatment?.map((t, i) => (
                                    <li key={i} className="flex items-start gap-3 text-sm">
                                        <span className="w-5 h-5 bg-red-100 text-red-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                                        <span className="text-gray-600">{t}</span>
                                    </li>
                                ))}
                            </ol>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Prevention */}
            <div className="card overflow-hidden">
                <button onClick={() => setShowPrevention(!showPrevention)}
                    className="w-full flex items-center justify-between p-5 text-left hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-green-100 text-green-600 rounded-lg flex items-center justify-center">
                            <Shield size={14} />
                        </div>
                        <span className="font-semibold text-gray-900">Prevention Tips</span>
                    </div>
                    {showPrevention ? <ChevronUp size={18} className="text-gray-400" /> : <ChevronDown size={18} className="text-gray-400" />}
                </button>
                <AnimatePresence>
                    {showPrevention && (
                        <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                            <ul className="px-5 pb-5 space-y-2">
                                {result.prevention?.map((p, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm">
                                        <CheckCircle size={14} className="text-green-500 flex-shrink-0 mt-0.5" />
                                        <span className="text-gray-600">{p}</span>
                                    </li>
                                ))}
                            </ul>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <button onClick={onScanAnother} className="btn-secondary w-full justify-center">
                Scan Another Image
            </button>
        </motion.div>
    );
}

export default function DiseaseDetection() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const onDrop = useCallback((acceptedFiles) => {
        const f = acceptedFiles[0];
        if (!f) return;
        setFile(f);
        setResult(null);
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result);
        reader.readAsDataURL(f);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop, accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
        maxSize: 10 * 1024 * 1024, maxFiles: 1,
        onDropRejected: (files) => toast.error(files[0]?.errors[0]?.message || 'Invalid file')
    });

    const handleDetect = async () => {
        if (!file) return;
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await diseaseApi.detect(formData);
            setResult(res.data);
            toast.success('Analysis complete!');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Detection failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => { setFile(null); setPreview(null); setResult(null); };

    return (
        <div>
            <div className="page-header">
                <h1 className="section-title">Disease Detection</h1>
                <p className="section-subtitle">Upload a crop leaf image to detect diseases instantly</p>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Upload Column */}
                <div className="space-y-4">
                    <div className="card p-6">
                        {!preview ? (
                            <div {...getRootProps()}
                                className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${isDragActive ? 'border-green-400 bg-green-50 drag-active' : 'border-gray-200 hover:border-green-400 hover:bg-green-50'}`}>
                                <input {...getInputProps()} />
                                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <Upload size={28} />
                                </div>
                                <p className="font-semibold text-gray-900 text-lg mb-2">
                                    {isDragActive ? 'Drop the image here!' : 'Drag & drop leaf image here'}
                                </p>
                                <p className="text-sm text-gray-500 mb-4">or click to browse files</p>
                                <p className="text-xs text-gray-400">Accepts JPG, PNG, WEBP • Max 10MB</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="relative rounded-2xl overflow-hidden">
                                    <img src={preview} alt="Preview" className="w-full h-64 object-cover" />
                                    <button onClick={handleReset}
                                        className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center text-gray-600 hover:text-red-500 transition-colors">
                                        <X size={16} />
                                    </button>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-gray-600 font-medium truncate">{file.name}</span>
                                    <span className="text-gray-400 flex-shrink-0 ml-2">{fileSizeStr(file.size)}</span>
                                </div>
                                <button onClick={handleDetect} disabled={loading}
                                    className="btn-primary w-full justify-center py-3.5 text-base">
                                    {loading ? (
                                        <><div className="w-5 h-5 spinner border-white border-t-transparent" /> Analyzing your crop...</>
                                    ) : (
                                        <><Leaf size={20} /> Detect Disease</>
                                    )}
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Tips */}
                    <div className="card p-5 bg-green-50 border border-green-100">
                        <h4 className="font-semibold text-green-900 mb-2 text-sm">📸 Tips for best results</h4>
                        <ul className="space-y-1">
                            {['Take a clear, well-lit photo of a single leaf', 'Ensure the leaf fills most of the frame', 'Avoid blurry or dark images', 'Include the affected area if disease is suspected'].map(t => (
                                <li key={t} className="text-xs text-green-700 flex items-start gap-1.5"><span className="text-green-500 mt-0.5">•</span>{t}</li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Results Column */}
                <div>
                    {!result && !loading && (
                        <div className="card p-8 h-full flex flex-col items-center justify-center text-center">
                            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
                                <Leaf size={28} className="text-gray-400" />
                            </div>
                            <h3 className="font-semibold text-gray-700 mb-2">Results will appear here</h3>
                            <p className="text-sm text-gray-400">Upload an image and click "Detect Disease" to begin</p>
                        </div>
                    )}
                    {loading && (
                        <div className="card p-8 h-full flex flex-col items-center justify-center">
                            <div className="w-16 h-16 spinner mx-auto mb-4"></div>
                            <p className="font-semibold text-gray-700">Analyzing your crop...</p>
                            <p className="text-sm text-gray-400 mt-1">AI model is processing the image</p>
                        </div>
                    )}
                    {result && <DiseaseResult result={result} onScanAnother={handleReset} />}
                </div>
            </div>
        </div>
    );
}
