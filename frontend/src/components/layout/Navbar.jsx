import { Link, useNavigate } from 'react-router-dom';
import { Bell, Sprout } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getInitials } from '../../utils/helpers';

export default function Navbar() {
    const { user } = useAuth();
    const navigate = useNavigate();
    return (
        <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 sticky top-0 z-20 shadow-sm">
            <div className="flex items-center gap-2 lg:hidden">
                <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                    <Sprout size={16} className="text-white" />
                </div>
                <span className="font-bold text-gray-900 text-sm">AgroVision AI</span>
            </div>
            <div className="hidden lg:block" />
            <div className="flex items-center gap-3">
                <button
                    onClick={() => navigate('/profile')}
                    className="w-9 h-9 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold hover:bg-green-700 transition-colors"
                    title={user?.full_name}
                >
                    {getInitials(user?.full_name)}
                </button>
            </div>
        </header>
    );
}
