import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  icon: LucideIcon;
  variant?: 'sky' | 'emerald' | 'amber' | 'indigo';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  subtext,
  icon: Icon,
  variant = 'sky',
}) => {
  const variantStyles = {
    sky: 'from-sky-500/10 to-blue-500/5 border-sky-500/30 text-sky-400',
    emerald: 'from-emerald-500/10 to-teal-500/5 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/10 to-orange-500/5 border-amber-500/30 text-amber-400',
    indigo: 'from-indigo-500/10 to-purple-500/5 border-indigo-500/30 text-indigo-400',
  };

  const iconBgStyles = {
    sky: 'bg-sky-500/20 text-sky-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    amber: 'bg-amber-500/20 text-amber-400',
    indigo: 'bg-indigo-500/20 text-indigo-400',
  };

  return (
    <div className={`p-4 rounded-xl border bg-gradient-to-br glass-card transition-all ${variantStyles[variant]}`}>
      <div className="flex items-center justify-between gap-3 mb-2">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg ${iconBgStyles[variant]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {unit && <span className="text-xs font-semibold text-slate-400">{unit}</span>}
      </div>
      {subtext && <p className="text-[11px] text-slate-400 mt-1.5 line-clamp-1">{subtext}</p>}
    </div>
  );
};
