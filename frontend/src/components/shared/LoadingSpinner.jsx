import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers';

export default function LoadingSpinner({ size = 'md', text = '', className = '' }) {
    const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' };
    return (
        <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
            <div className={cn('spinner', sizes[size])}></div>
            {text && <p className="text-sm text-gray-500 font-medium">{text}</p>}
        </div>
    );
}
