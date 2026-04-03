import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LayoutDashboard, Leaf, TrendingUp, History, User,
    LogOut, Menu, X, ChevronRight, Sprout
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getInitials } from '../../utils/helpers';
import toast from 'react-hot-toast';

const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/detect', icon: Leaf, label: 'Disease Detection' },
    { to: '/yield', icon: TrendingUp, label: 'Yield Prediction' },
    { to: '/history', icon: History, label: 'History' },
    { to: '/profile', icon: User, label: 'Profile' },
];

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        toast.success('Logged out successfully');
        navigate('/');
    };

    return (
        <motion.aside
            initial={false}
            animate={{ width: collapsed ? 72 : 256 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="h-screen bg-white border-r border-gray-100 flex flex-col overflow-hidden shadow-sm relative z-10 flex-shrink-0"
        >
            {/* Logo */}
            <div className="p-4 flex items-center gap-3 border-b border-gray-100 h-16">
                <div className="w-9 h-9 bg-green-600 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Sprout size={20} className="text-white" />
                </div>
                <AnimatePresence>
                    {!collapsed && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            <span className="font-bold text-gray-900 text-sm leading-tight">AgroVision</span>
                            <span className="block text-xs text-green-600 font-medium">AI Platform</span>
                        </motion.div>
                    )}
                </AnimatePresence>
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="ml-auto rounded-lg p-1.5 hover:bg-gray-100 transition-colors text-gray-500"
                >
                    {collapsed ? <ChevronRight size={16} /> : <Menu size={16} />}
                </button>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `nav-link ${isActive ? 'active' : ''} ${collapsed ? 'justify-center px-2' : ''}`
                        }
                        title={collapsed ? label : ''}
                    >
                        <Icon size={20} className="flex-shrink-0" />
                        <AnimatePresence>
                            {!collapsed && (
                                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                    className="text-sm">
                                    {label}
                                </motion.span>
                            )}
                        </AnimatePresence>
                    </NavLink>
                ))}
            </nav>

            {/* User */}
            <div className="p-3 border-t border-gray-100">
                <button
                    onClick={handleLogout}
                    className={`nav-link w-full text-red-500 hover:bg-red-50 hover:text-red-600 ${collapsed ? 'justify-center px-2' : ''}`}
                    title="Logout"
                >
                    <LogOut size={20} className="flex-shrink-0" />
                    <AnimatePresence>
                        {!collapsed && (
                            <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                className="text-sm">
                                Logout
                            </motion.span>
                        )}
                    </AnimatePresence>
                </button>
                {!collapsed && user && (
                    <div className="flex items-center gap-3 p-3 mt-2 bg-green-50 rounded-xl">
                        <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                            {getInitials(user.full_name)}
                        </div>
                        <div className="min-w-0">
                            <p className="text-xs font-semibold text-gray-900 truncate">{user.full_name}</p>
                            <p className="text-xs text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                )}
            </div>
        </motion.aside>
    );
}
