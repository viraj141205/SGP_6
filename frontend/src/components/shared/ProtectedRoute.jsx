import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-green-50">
                <div className="text-center">
                    <div className="w-12 h-12 spinner mx-auto mb-4"></div>
                    <p className="text-green-700 font-medium">Loading AgroVision...</p>
                </div>
            </div>
        );
    }

    return user ? children : <Navigate to="/login" replace />;
}
