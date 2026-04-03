import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts';

export default function ComparisonBarChart({ predicted, average, best }) {
    const data = [
        { name: 'Predicted', value: predicted, color: '#16a34a' },
        { name: 'Average', value: average, color: '#f59e0b' },
        { name: 'Best Possible', value: best || predicted * 1.3, color: '#3b82f6' },
    ];

    return (
        <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data} barSize={40}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#6b7280' }} />
                <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
                <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                    formatter={(v) => [`${v.toFixed(2)} q/acre`, 'Yield']}
                />
                {data.map((entry, index) => (
                    <Bar key={entry.name} dataKey="value" data={[entry]} fill={entry.color} radius={[6, 6, 0, 0]} />
                ))}
                <Bar dataKey="value" data={data} radius={[6, 6, 0, 0]}>
                    {data.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}
