import { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Lock, Trash2, Shield, Save, Eye, EyeOff } from 'lucide-react';
import { authApi } from '../api/authApi';
import { useAuth } from '../context/AuthContext';
import { formatDate, getInitials } from '../utils/helpers';
import toast from 'react-hot-toast';

const profileSchema = z.object({
    full_name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Invalid email'),
});

const passwordSchema = z.object({
    current_password: z.string().min(1, 'Current password required'),
    new_password: z.string().min(6, 'New password must be at least 6 characters'),
    confirm_password: z.string(),
}).refine(d => d.new_password === d.confirm_password, {
    message: "Passwords don't match", path: ['confirm_password']
});

export default function Profile() {
    const { user, updateUser, logout } = useAuth();
    const [showPwd, setShowPwd] = useState(false);
    const [deleteConfirm, setDeleteConfirm] = useState(false);
    const [tab, setTab] = useState('profile');

    const profileForm = useForm({
        resolver: zodResolver(profileSchema),
        defaultValues: { full_name: user?.full_name || '', email: user?.email || '' },
    });

    const passwordForm = useForm({
        resolver: zodResolver(passwordSchema),
    });

    const onProfileSave = async (data) => {
        try {
            const res = await authApi.updateMe(data);
            updateUser(res.data);
            toast.success('Profile updated successfully!');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to update profile');
        }
    };

    const onPasswordChange = async (data) => {
        try {
            await authApi.changePassword({ current_password: data.current_password, new_password: data.new_password });
            toast.success('Password changed successfully!');
            passwordForm.reset();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to change password');
        }
    };

    const handleDeleteAccount = async () => {
        try {
            await authApi.deleteAccount();
            logout();
            toast.success('Account deleted.');
        } catch {
            toast.error('Failed to delete account');
        }
    };

    const tabs = [
        { id: 'profile', icon: <User size={16} />, label: 'Profile' },
        { id: 'security', icon: <Lock size={16} />, label: 'Security' },
        { id: 'danger', icon: <Shield size={16} />, label: 'Account' },
    ];

    return (
        <div>
            <div className="page-header">
                <h1 className="section-title">Profile</h1>
                <p className="section-subtitle">Manage your account information</p>
            </div>

            <div className="grid lg:grid-cols-4 gap-6">
                {/* Avatar Column */}
                <div className="lg:col-span-1">
                    <div className="card p-6 text-center">
                        <div className="w-20 h-20 bg-green-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                            {getInitials(user?.full_name)}
                        </div>
                        <p className="font-bold text-gray-900">{user?.full_name}</p>
                        <p className="text-sm text-gray-500 truncate">{user?.email}</p>
                        <p className="text-xs text-gray-400 mt-3">Member since {formatDate(user?.created_at)}</p>

                        <div className="border-t border-gray-100 mt-4 pt-4">
                            {tabs.map(t => (
                                <button key={t.id} onClick={() => setTab(t.id)}
                                    className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors mb-1 ${tab === t.id ? 'bg-green-100 text-green-700' : 'text-gray-600 hover:bg-gray-50'}`}>
                                    {t.icon}{t.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Content Column */}
                <div className="lg:col-span-3">
                    {tab === 'profile' && (
                        <motion.div key="profile" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="card p-6">
                            <h2 className="font-bold text-gray-900 mb-5 text-lg">Edit Profile</h2>
                            <form onSubmit={profileForm.handleSubmit(onProfileSave)} className="space-y-5">
                                <div>
                                    <label className="label">Full Name</label>
                                    <div className="relative">
                                        <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                        <input {...profileForm.register('full_name')} className="input-field pl-10" placeholder="Your full name" />
                                    </div>
                                    {profileForm.formState.errors.full_name && (
                                        <p className="text-red-500 text-xs mt-1">{profileForm.formState.errors.full_name.message}</p>
                                    )}
                                </div>
                                <div>
                                    <label className="label">Email Address</label>
                                    <div className="relative">
                                        <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                        <input {...profileForm.register('email')} type="email" className="input-field pl-10" placeholder="your@email.com" />
                                    </div>
                                    {profileForm.formState.errors.email && (
                                        <p className="text-red-500 text-xs mt-1">{profileForm.formState.errors.email.message}</p>
                                    )}
                                </div>
                                <button type="submit" disabled={profileForm.formState.isSubmitting} className="btn-primary">
                                    {profileForm.formState.isSubmitting ? <><div className="w-4 h-4 spinner border-white border-t-transparent" />Saving...</> : <><Save size={16} />Save Changes</>}
                                </button>
                            </form>
                        </motion.div>
                    )}

                    {tab === 'security' && (
                        <motion.div key="security" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="card p-6">
                            <h2 className="font-bold text-gray-900 mb-5 text-lg">Change Password</h2>
                            <form onSubmit={passwordForm.handleSubmit(onPasswordChange)} className="space-y-5">
                                {[
                                    { name: 'current_password', label: 'Current Password', placeholder: '••••••••' },
                                    { name: 'new_password', label: 'New Password', placeholder: 'At least 6 characters' },
                                    { name: 'confirm_password', label: 'Confirm New Password', placeholder: '••••••••' },
                                ].map(field => (
                                    <div key={field.name}>
                                        <label className="label">{field.label}</label>
                                        <div className="relative">
                                            <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                            <input
                                                {...passwordForm.register(field.name)}
                                                type={showPwd ? 'text' : 'password'}
                                                className="input-field pl-10 pr-10"
                                                placeholder={field.placeholder}
                                            />
                                            {field.name === 'new_password' && (
                                                <button type="button" onClick={() => setShowPwd(!showPwd)}
                                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                                                    {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                                                </button>
                                            )}
                                        </div>
                                        {passwordForm.formState.errors[field.name] && (
                                            <p className="text-red-500 text-xs mt-1">{passwordForm.formState.errors[field.name].message}</p>
                                        )}
                                    </div>
                                ))}
                                <button type="submit" disabled={passwordForm.formState.isSubmitting} className="btn-primary">
                                    {passwordForm.formState.isSubmitting ? <><div className="w-4 h-4 spinner border-white border-t-transparent" />Changing...</> : <><Lock size={16} />Change Password</>}
                                </button>
                            </form>
                        </motion.div>
                    )}

                    {tab === 'danger' && (
                        <motion.div key="danger" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="card p-6 border-2 border-red-100">
                            <h2 className="font-bold text-red-700 mb-2 text-lg">Danger Zone</h2>
                            <p className="text-sm text-gray-500 mb-6">These actions are irreversible. Please be certain.</p>
                            <div className="bg-red-50 border border-red-200 rounded-xl p-5">
                                <h3 className="font-semibold text-red-800 mb-1">Delete Account</h3>
                                <p className="text-sm text-red-600 mb-4">All your data, history, and predictions will be permanently deleted.</p>
                                {!deleteConfirm ? (
                                    <button onClick={() => setDeleteConfirm(true)} className="btn-danger flex items-center gap-2">
                                        <Trash2 size={16} /> Delete My Account
                                    </button>
                                ) : (
                                    <div className="space-y-3">
                                        <p className="text-sm font-semibold text-red-800">Are you absolutely sure?</p>
                                        <div className="flex gap-3">
                                            <button onClick={handleDeleteAccount} className="btn-danger">Yes, Delete Forever</button>
                                            <button onClick={() => setDeleteConfirm(false)} className="btn-secondary">Cancel</button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>
        </div>
    );
}
