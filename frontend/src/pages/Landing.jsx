import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Leaf, TrendingUp, ShieldCheck, Zap, Users, Award, ArrowRight, CheckCircle, Sprout } from 'lucide-react';

const features = [
    { icon: <Leaf size={24} />, title: 'Disease Detection', desc: 'Upload a leaf photo and get instant AI-powered disease diagnosis with treatment recommendations.' },
    { icon: <TrendingUp size={24} />, title: 'Yield Prediction', desc: 'Enter your farm parameters and receive accurate yield forecasts with actionable recommendations.' },
    { icon: <ShieldCheck size={24} />, title: '38+ Diseases Covered', desc: 'Trained on 54,000+ images across 14 crop types with 95%+ accuracy using EfficientNetB3.' },
    { icon: <Zap size={24} />, title: 'Instant Results', desc: 'Get disease diagnosis in under 5 seconds and yield predictions powered by ensemble ML models.' },
];

const steps = [
    { num: '01', title: 'Upload or Input', desc: 'Upload a leaf photo or enter your farm parameters' },
    { num: '02', title: 'AI Analysis', desc: 'Our models analyze your data with 95%+ accuracy' },
    { num: '03', title: 'Take Action', desc: 'Get treatment plans, prevention tips & yield forecasts' },
];

const testimonials = [
    { name: 'Rajan Patel', location: 'Gujarat, India', quote: 'AgroVision detected early blight in my tomatoes before I could see any symptoms. Saved my entire harvest!' },
    { name: 'Suresh Kumar', location: 'Punjab, India', quote: 'The yield prediction was spot on. I adjusted my irrigation and got 22% more wheat than last year.' },
    { name: 'Priya Nair', location: 'Kerala, India', quote: 'Easy to use on my phone in the field. The AI knows more about plant diseases than I do!' },
];

export default function Landing() {
    return (
        <div className="min-h-screen bg-white font-sans">
            {/* Navbar */}
            <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                            <Sprout size={18} className="text-white" />
                        </div>
                        <span className="font-bold text-gray-900">AgroVision AI</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <Link to="/login" className="text-gray-600 hover:text-green-600 font-medium text-sm transition-colors">Login</Link>
                        <Link to="/register" className="btn-primary text-sm py-2 px-4">Get Started</Link>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <section className="animated-gradient min-h-screen flex items-center relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                    {[...Array(20)].map((_, i) => (
                        <div key={i} className="absolute rounded-full border border-white"
                            style={{
                                width: `${Math.random() * 200 + 50}px`, height: `${Math.random() * 200 + 50}px`,
                                top: `${Math.random() * 100}%`, left: `${Math.random() * 100}%`,
                                opacity: Math.random() * 0.5
                            }}
                        />
                    ))}
                </div>
                <div className="max-w-7xl mx-auto px-6 py-20 relative z-10">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.7 }}>
                            <div className="inline-flex items-center gap-2 bg-white/20 text-white px-4 py-2 rounded-full text-sm font-medium mb-6 backdrop-blur-sm">
                                <span className="w-2 h-2 bg-green-300 rounded-full animate-pulse" />
                                AI-Powered Agriculture Platform
                            </div>
                            <h1 className="text-5xl lg:text-6xl font-black text-white leading-tight mb-6">
                                AI-Powered<br />
                                <span className="text-green-300">Crop Intelligence</span>
                            </h1>
                            <p className="text-xl text-white/80 mb-8 leading-relaxed">
                                Detect diseases instantly. Predict yields accurately.<br />
                                Empower your farming decisions with AI.
                            </p>
                            <div className="flex gap-4 flex-wrap">
                                <Link to="/register" className="inline-flex items-center gap-2 bg-white text-green-700 font-bold px-8 py-4 rounded-2xl hover:bg-green-50 transition-all shadow-lg hover:shadow-xl text-lg">
                                    Start Detecting <ArrowRight size={20} />
                                </Link>
                                <Link to="/register" className="inline-flex items-center gap-2 glass-card text-white font-bold px-8 py-4 rounded-2xl hover:bg-white/20 transition-all text-lg">
                                    Predict Yield
                                </Link>
                            </div>
                        </motion.div>
                        <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.7, delay: 0.2 }}
                            className="hidden lg:flex justify-center">
                            <div className="relative">
                                <div className="w-80 h-80 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20">
                                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                                        className="absolute inset-4 rounded-full border-2 border-dashed border-green-300/40" />
                                    <motion.div animate={{ y: [-10, 10, -10] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}>
                                        <Leaf size={120} className="text-green-300" />
                                    </motion.div>
                                </div>
                                {[
                                    { icon: <CheckCircle size={20} />, text: '95% Accuracy', pos: 'top-4 right-0' },
                                    { icon: <Zap size={20} />, text: 'Instant Results', pos: 'bottom-4 left-0' },
                                    { icon: <Award size={20} />, text: '38+ Diseases', pos: 'top-1/2 -left-12' },
                                ].map((badge, i) => (
                                    <motion.div key={i} animate={{ y: [-5, 5, -5] }} transition={{ duration: 2.5, repeat: Infinity, delay: i * 0.5 }}
                                        className={`absolute ${badge.pos} bg-white rounded-2xl px-4 py-2 shadow-xl flex items-center gap-2 text-green-700 font-semibold text-sm`}>
                                        {badge.icon}{badge.text}
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="bg-green-600 py-12">
                <div className="max-w-4xl mx-auto px-6 grid grid-cols-3 gap-8 text-center">
                    {[
                        { value: '98.5%', label: 'Model Accuracy' },
                        { value: '38+', label: 'Diseases Covered' },
                        { value: '50K+', label: 'Farmers Using AI' },
                    ].map((s, i) => (
                        <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                            <p className="text-4xl font-black text-white">{s.value}</p>
                            <p className="text-green-200 mt-1 text-sm font-medium">{s.label}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section className="py-20 bg-green-50">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">Everything you need to farm smarter</h2>
                        <p className="text-gray-500 text-lg">Powered by state-of-the-art machine learning models</p>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {features.map((f, i) => (
                            <motion.div key={i} whileHover={{ y: -6, scale: 1.02 }} transition={{ type: 'spring', stiffness: 300 }}
                                className="card p-6 hover:shadow-xl transition-shadow">
                                <div className="w-12 h-12 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mb-4">
                                    {f.icon}
                                </div>
                                <h3 className="font-bold text-gray-900 mb-2">{f.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 bg-white">
                <div className="max-w-5xl mx-auto px-6">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
                        <p className="text-gray-500">Three simple steps to actionable insights</p>
                    </div>
                    <div className="grid md:grid-cols-3 gap-8 relative">
                        <div className="hidden md:block absolute top-8 left-1/4 right-1/4 h-0.5 bg-green-200" />
                        {steps.map((s, i) => (
                            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.15 }}
                                className="text-center">
                                <div className="w-16 h-16 bg-green-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 text-xl font-black shadow-lg shadow-green-200">
                                    {s.num}
                                </div>
                                <h3 className="font-bold text-gray-900 text-lg mb-2">{s.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">{s.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="py-20 bg-green-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">Trusted by Farmers</h2>
                    </div>
                    <div className="grid md:grid-cols-3 gap-6">
                        {testimonials.map((t, i) => (
                            <motion.div key={i} whileHover={{ y: -4 }} className="card p-6">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">
                                        {t.name[0]}
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-900 text-sm">{t.name}</p>
                                        <p className="text-xs text-gray-500">{t.location}</p>
                                    </div>
                                </div>
                                <p className="text-gray-600 text-sm leading-relaxed italic">"{t.quote}"</p>
                                <div className="flex mt-3">
                                    {[...Array(5)].map((_, j) => (
                                        <span key={j} className="text-amber-400 text-sm">★</span>
                                    ))}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="gradient-bg py-20 text-center">
                <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}>
                    <h2 className="text-4xl font-bold text-white mb-4">Ready to farm smarter?</h2>
                    <p className="text-white/80 mb-8 text-lg">Start detecting diseases and predicting yields in minutes.</p>
                    <Link to="/register" className="inline-flex items-center gap-2 bg-white text-green-700 font-bold px-10 py-4 rounded-2xl hover:bg-green-50 transition-all shadow-xl text-lg">
                        Get Started Free <ArrowRight size={20} />
                    </Link>
                </motion.div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-400 py-10">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-green-600 rounded-lg flex items-center justify-center">
                            <Sprout size={14} className="text-white" />
                        </div>
                        <span className="text-white font-bold">AgroVision AI</span>
                    </div>
                    <p className="text-sm">© 2025 AgroVision AI. Built for farmers, by AI engineers.</p>
                    <div className="flex gap-4 text-sm">
                        <Link to="/login" className="hover:text-white transition-colors">Login</Link>
                        <Link to="/register" className="hover:text-white transition-colors">Register</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}
