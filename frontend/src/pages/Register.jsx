import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Sprout, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const schema = z.object({
    full_name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    confirm_password: z.string(),
}).refine(d => d.password === d.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
});

function PasswordStrength({ password }) {
    const strength = !password ? 0 :
        password.length >= 12 && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[^a-zA-Z0-9]/.test(password) ? 4 :
            password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password) ? 3 :
                password.length >= 6 ? 2 : 1;
    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['', 'bg-red-400', 'bg-amber-400', 'bg-blue-400', 'bg-green-500'];
    return (
        <div className="mt-2">
            <div className="flex gap-1 h-1.5 mb-1">
                {[1, 2, 3, 4].map(i => (
                    <div key={i} className={`flex-1 rounded-full transition-all ${i <= strength ? colors[strength] : 'bg-gray-200'}`} />
                ))}
            </div>
            {strength > 0 && <p className={`text-xs font-medium ${['', 'text-red-500', 'text-amber-500', 'text-blue-500', 'text-green-600'][strength]}`}>{labels[strength]}</p>}
        </div>
    );
}

export default function Register() {
    const [showPwd, setShowPwd] = useState(false);
    const [watchPwd, setWatchPwd] = useState('');
    const { register: authRegister } = useAuth();
    const navigate = useNavigate();

    const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm({
        resolver: zodResolver(schema),
    });

    const password = watch('password', '');

    const onSubmit = async (data) => {
        try {
            await authRegister(data.email, data.password, data.full_name);
            toast.success('Account created! Welcome to AgroVision 🌱');
            navigate('/dashboard');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Registration failed. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-green-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
                className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-2xl mb-4 shadow-lg shadow-green-200">
                        <Sprout size={32} className="text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900">Create account</h1>
                    <p className="text-gray-500 mt-1">Join AgroVision AI for smarter farming</p>
                </div>

                <div className="card p-8">
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        <div>
                            <label className="label">Full Name</label>
                            <input {...register('full_name')} className="input-field" placeholder="John Farmer" />
                            {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message}</p>}
                        </div>
                        <div>
                            <label className="label">Email Address</label>
                            <input {...register('email')} type="email" className="input-field" placeholder="you@example.com" />
                            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
                        </div>
                        <div>
                            <label className="label">Password</label>
                            <div className="relative">
                                <input {...register('password')} type={showPwd ? 'text' : 'password'}
                                    className="input-field pr-12" placeholder="••••••••" />
                                <button type="button" onClick={() => setShowPwd(!showPwd)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                    {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                            <PasswordStrength password={password} />
                            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
                        </div>
                        <div>
                            <label className="label">Confirm Password</label>
                            <input {...register('confirm_password')} type="password" className="input-field" placeholder="••••••••" />
                            {errors.confirm_password && <p className="text-red-500 text-xs mt-1">{errors.confirm_password.message}</p>}
                        </div>

                        <button type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center py-3.5 text-base">
                            {isSubmitting ? (
                                <><div className="w-5 h-5 spinner border-white border-t-transparent" /> Creating account...</>
                            ) : (
                                <>Create Account <ArrowRight size={18} /></>
                            )}
                        </button>
                    </form>
                    <p className="text-center text-sm text-gray-500 mt-6">
                        Already have an account?{' '}
                        <Link to="/login" className="text-green-600 font-semibold hover:underline">Sign in</Link>
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
