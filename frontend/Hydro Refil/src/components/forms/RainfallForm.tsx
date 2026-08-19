import React from 'react';
import { CloudRain, Info, Database } from 'lucide-react';
import { RainfallInput } from '../../types';

interface RainfallFormProps {
  data: RainfallInput;
  onChange: (fields: Partial<RainfallInput>) => void;
}

export const RainfallForm: React.FC<RainfallFormProps> = ({ data, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <CloudRain className="w-3.5 h-3.5 text-sky-400" />
            Normal Annual Rainfall *
          </span>
          <span className="text-[11px] text-slate-400 font-mono">Millimetres (mm/year)</span>
        </label>
        <div className="relative">
          <input
            type="number"
            min="50"
            max="15000"
            step="any"
            required
            value={data.annual_mm || ''}
            onChange={(e) => onChange({ annual_mm: parseFloat(e.target.value) || 0 })}
            placeholder="e.g. 1200"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono font-semibold focus:border-sky-500 pr-14"
          />
          <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-mono pointer-events-none">
            mm/yr
          </span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1">
          Source: {data.data_source === 'imd_database' ? 'IMD Climatological Normal Table' : 'Manual Field Entry / Regional Rain Gauge'}
        </p>
      </div>

      <div className="p-3 rounded-lg bg-sky-950/30 border border-sky-800/40 text-xs text-sky-200/90 leading-relaxed flex items-start gap-2">
        <Info className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-sky-100 block mb-0.5">Hydrological Rainfall Standard:</strong>
          Rainfall data is automatically distributed across 12 calendar months according to the standard Indian South-West Monsoon hydrograph (June–September peak), unless custom monthly rain gauge values are configured.
        </div>
      </div>
    </div>
  );
};
