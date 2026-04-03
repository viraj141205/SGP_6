import { motion } from 'framer-motion';

export default function StatCard({ icon, label, value, trend, color = 'green', numericValue }) {
    const colors = {
        green: 'bg-green-100 text-green-600',
        blue: 'bg-blue-100 text-blue-600',
        amber: 'bg-amber-100 text-amber-600',
        red: 'bg-red-100 text-red-600',
        purple: 'bg-purple-100 text-purple-600',
    };

    return (
        <motion.div
            whileHover={{ scale: 1.02, y: -2 }}
            transition={{ type: 'spring', stiffness: 300 }}
            className="stat-card"
        >
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-gray-500 font-medium mb-1">{label}</p>
                    <p className="text-3xl font-bold text-gray-900">
                        {numericValue !== undefined ? (
                            <span>{numericValue.toLocaleString()}</span>
                        ) : value}
                    </p>
                    {trend && (
                        <p className={`text-xs mt-1.5 font-medium ${trend.startsWith('+') ? 'text-green-600' : 'text-red-500'}`}>
                            {trend} vs last month
                        </p>
                    )}
                </div>
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${colors[color]}`}>
                    {icon}
                </div>
            </div>
        </motion.div>
    );
}
