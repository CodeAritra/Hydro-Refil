import React from 'react';
import { AlertTriangle, Info, ShieldAlert } from 'lucide-react';

interface WarningsAlertProps {
  warnings: string[];
}

export const WarningsAlert: React.FC<WarningsAlertProps> = ({ warnings }) => {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
      <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
        <AlertTriangle className="w-4 h-4" />
        <span>Engineering Warnings & Site Constraints ({warnings.length})</span>
      </div>
      <ul className="space-y-1.5 text-xs text-amber-200/90 pl-5 list-disc">
        {warnings.map((w, i) => (
          <li key={i}>{w}</li>
        ))}
      </ul>
    </div>
  );
};
