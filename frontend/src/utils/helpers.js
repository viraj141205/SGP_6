import { formatDistanceToNow, format } from 'date-fns';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export function timeAgo(dateString) {
    try {
        return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
        return 'Unknown time';
    }
}

export function formatDate(dateString) {
    try {
        return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
        return 'N/A';
    }
}

export function formatDateTime(dateString) {
    try {
        return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch {
        return 'N/A';
    }
}

export function formatConfidence(value) {
    return `${(value * 100).toFixed(1)}%`;
}

export function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
}

export function formatYield(value) {
    return value ? value.toFixed(2) : '0.00';
}

export function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

export function truncate(str, length = 50) {
    if (!str) return '';
    return str.length > length ? str.slice(0, length) + '...' : str;
}

export function fileSizeStr(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function getSeverityClass(severity) {
    const map = {
        None: 'badge-green',
        Low: 'badge-green',
        Medium: 'badge-amber',
        High: 'badge-red',
    };
    return map[severity] || 'badge-amber';
}

export function getPerformanceColor(rating) {
    const map = {
        Poor: '#ef4444',
        Average: '#f59e0b',
        Good: '#3b82f6',
        Excellent: '#16a34a',
    };
    return map[rating] || '#6b7280';
}
