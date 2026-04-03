export default function ConfidenceBar({ value, label, showPercent = true }) {
    const percent = Math.round(value * 100);
    const color = percent >= 85 ? 'bg-green-500' : percent >= 65 ? 'bg-amber-400' : 'bg-red-400';
    return (
        <div className="w-full">
            {label && (
                <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-gray-600 font-medium">{label}</span>
                    {showPercent && <span className="font-bold text-gray-900">{percent}%</span>}
                </div>
            )}
            <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-700 ${color}`}
                    style={{ width: `${percent}%` }}
                />
            </div>
        </div>
    );
}
