import React from 'react';
import { Users, Droplets, PieChart, ShieldCheck } from 'lucide-react';
import { WaterDemandInput } from '../../types';

interface DemandFormProps {
  data: WaterDemandInput;
  onChange: (fields: Partial<WaterDemandInput>) => void;
}

export const DemandForm: React.FC<DemandFormProps> = ({ data, onChange }) => {
  const demandPresets = [
    { label: 'Urban Domestic (135 LPCD — IS 1172)', lpcd: 135, type: 'domestic_urban' },
    { label: 'Rural Domestic (70 LPCD — JJM)', lpcd: 70, type: 'domestic_rural' },
    { label: 'Day School / Office (45 LPCD)', lpcd: 45, type: 'school_office' },
    { label: 'Hostel / Institutional (135 LPCD)', lpcd: 135, type: 'hostel' },
  ];

  const estimatedDaily = (data.num_people || 0) * (data.per_capita_demand_lpd || 135);
  const estimatedAnnual = estimatedDaily * 365;
  const harvestablePortion = estimatedAnnual * (data.non_potable_fraction || 0.40);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Occupant count */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-sky-400" />
            Number of Inhabitants / Users
          </label>
          <input
            type="number"
            min="0"
            max="50000"
            value={data.num_people || ''}
            onChange={(e) => onChange({ num_people: parseInt(e.target.value, 10) || 0 })}
            placeholder="e.g. 6"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono font-semibold focus:border-sky-500"
          />
        </div>

        {/* Per-capita standard */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-sky-400" />
              Per Capita Standard
            </span>
            <span className="text-[11px] text-slate-400 font-mono">LPCD</span>
          </label>
          <select
            value={data.per_capita_demand_lpd || 135}
            onChange={(e) => onChange({ per_capita_demand_lpd: parseFloat(e.target.value) })}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:border-sky-500"
          >
            {demandPresets.map((p) => (
              <option key={p.label} value={p.lpcd}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Non-potable fraction slider */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <PieChart className="w-3.5 h-3.5 text-sky-400" />
            Non-Potable Harvestable Share
          </label>
          <span className="text-xs font-mono font-bold text-sky-400">
            {((data.non_potable_fraction || 0.4) * 100).toFixed(0)}% (Flushing, Gardening, Washing)
          </span>
        </div>
        <input
          type="range"
          min="0.1"
          max="1.0"
          step="0.05"
          value={data.non_potable_fraction || 0.4}
          onChange={(e) => onChange({ non_potable_fraction: parseFloat(e.target.value) })}
          className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500"
        />
        <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
          <span>10% (minimal non-potable)</span>
          <span>40% (typical IS 1172 norm)</span>
          <span>100% (total demand)</span>
        </div>
      </div>

      {/* Demand Summary Calculation Box */}
      {data.num_people > 0 && (
        <div className="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs space-y-1.5">
          <div className="flex justify-between text-slate-300">
            <span>Total Gross Demand:</span>
            <span className="font-mono font-bold text-white">{(estimatedAnnual / 1000).toFixed(1)} m³/year ({estimatedAnnual.toLocaleString()} L)</span>
          </div>
          <div className="flex justify-between text-sky-400 font-semibold border-t border-slate-700/80 pt-1.5">
            <span>Target Rainwater Harvest Demand:</span>
            <span className="font-mono font-bold">{(harvestablePortion / 1000).toFixed(1)} m³/year ({harvestablePortion.toLocaleString()} L)</span>
          </div>
        </div>
      )}
    </div>
  );
};
