import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

export default function YieldLineChart({ data = [] }) {
    if (!data.length) return (
        <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No predictions yet</div>
    );

    return (
        <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={data}>
                <defs>
                    <linearGradient id="yieldGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#16a34a" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                    formatter={(v) => [`${v.toFixed(2)} q/acre`, 'Yield']}
                />
                <Area type="monotone" dataKey="yield" stroke="#16a34a" strokeWidth={2.5} fill="url(#yieldGrad)" dot={{ fill: '#16a34a', r: 4 }} />
            </AreaChart>
        </ResponsiveContainer>
    );
}
