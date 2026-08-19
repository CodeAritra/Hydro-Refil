import React from 'react';
import { Shovel, Waves, Expand, AlertCircle, ShieldCheck } from 'lucide-react';
import { SiteConditionsInput, SoilTypeKey } from '../../types';
import soilData from '../../data/soil-types.json';

interface SiteConditionsFormProps {
  data: SiteConditionsInput;
  onChange: (fields: Partial<SiteConditionsInput>) => void;
}

export const SiteConditionsForm: React.FC<SiteConditionsFormProps> = ({ data, onChange }) => {
  const selectedSoil = soilData.find((s) => s.key === data.soil_type_key) || soilData[0];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Soil Type Selection */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Shovel className="w-3.5 h-3.5 text-sky-400" />
              Subsoil Classification
            </span>
            <span className="text-[11px] text-sky-400 font-mono">I = {selectedSoil.infiltration_rate_mm_hr} mm/hr</span>
          </label>
          <select
            value={data.soil_type_key}
            onChange={(e) => onChange({ soil_type_key: e.target.value as SoilTypeKey })}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:border-sky-500"
          >
            {soilData.map((s) => (
              <option key={s.key} value={s.key}>
                {s.display_name} ({s.infiltration_rate_mm_hr} mm/hr)
              </option>
            ))}
          </select>
        </div>

        {/* Groundwater Depth */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Waves className="w-3.5 h-3.5 text-sky-400" />
              Water Table Depth (BGL)
            </span>
            <span className="text-[11px] text-slate-400 font-mono">Metres BGL</span>
          </label>
          <div className="relative">
            <input
              type="number"
              min="0.5"
              max="150"
              step="0.5"
              value={data.groundwater_depth_mbgl ?? ''}
              onChange={(e) => {
                const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
                onChange({ groundwater_depth_mbgl: val });
              }}
              placeholder="e.g. 12.0"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono font-semibold focus:border-sky-500 pr-16"
            />
            <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-mono pointer-events-none">
              m BGL
            </span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            CGWB Minimum Safe Depth for Recharge Pit: 3.0 m
          </span>
        </div>
      </div>

      {/* Soil Description Card */}
      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs space-y-1.5">
        <div className="flex items-center justify-between text-slate-300">
          <span className="font-semibold text-slate-200">{selectedSoil.display_name}</span>
          <span className="text-sky-400 font-mono font-bold">Rate: {selectedSoil.infiltration_rate_mm_hr} mm/hr ({selectedSoil.range})</span>
        </div>
        <p className="text-slate-400 text-[11px]">{selectedSoil.description}</p>
        <div className="flex items-center gap-1 text-slate-400 text-[10px]">
          <ShieldCheck className="w-3 h-3 text-sky-400 flex-shrink-0" />
          <span>Source: {selectedSoil.source}</span>
        </div>
      </div>

      {/* Available Space */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Expand className="w-3.5 h-3.5 text-slate-400" />
            Available Open Land for Recharge Structure (Optional)
          </span>
          <span className="text-[11px] text-slate-400 font-mono">Square Metres (m²)</span>
        </label>
        <div className="relative">
          <input
            type="number"
            min="1"
            max="10000"
            value={data.available_area_m2 ?? ''}
            onChange={(e) => {
              const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
              onChange({ available_area_m2: val });
            }}
            placeholder="e.g. 25 (garden or open yard space)"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono focus:border-sky-500 pr-12"
          />
          <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-mono pointer-events-none">
            m²
          </span>
        </div>
      </div>
    </div>
  );
};
