import React from 'react';
import { Home, Layers, ArrowUpRight, ShieldCheck } from 'lucide-react';
import { RoofInput, RoofMaterialKey } from '../../types';
import runoffData from '../../data/runoff-coefficients.json';

interface RoofFormProps {
  data: RoofInput;
  onChange: (fields: Partial<RoofInput>) => void;
}

export const RoofForm: React.FC<RoofFormProps> = ({ data, onChange }) => {
  const selectedMaterial = runoffData.find((m) => m.key === data.material_key) || runoffData[0];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Roof Area */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Home className="w-3.5 h-3.5 text-sky-400" />
              Catchment / Rooftop Area *
            </span>
            <span className="text-[11px] text-slate-400 font-mono">Square Metres (m²)</span>
          </label>
          <div className="relative">
            <input
              type="number"
              min="1"
              max="50000"
              step="any"
              required
              value={data.area_m2 || ''}
              onChange={(e) => onChange({ area_m2: parseFloat(e.target.value) || 0 })}
              placeholder="e.g. 250"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono font-semibold focus:border-sky-500 pr-12"
            />
            <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-mono pointer-events-none">
              m²
            </span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            ≈ {((data.area_m2 || 0) * 10.7639).toFixed(0)} sq.ft
          </span>
        </div>

        {/* Roof Material */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-sky-400" />
              Roofing Material
            </span>
            <span className="text-[11px] text-sky-400 font-mono">C = {selectedMaterial.value}</span>
          </label>
          <select
            value={data.material_key}
            onChange={(e) => onChange({ material_key: e.target.value as RoofMaterialKey })}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:border-sky-500"
          >
            {runoffData.map((m) => (
              <option key={m.key} value={m.key}>
                {m.display_name} (C = {m.value})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Selected Material Information Card */}
      <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs space-y-1.5">
        <div className="flex items-center justify-between text-slate-300">
          <span className="font-semibold text-slate-200">{selectedMaterial.display_name}</span>
          <span className="text-emerald-400 font-mono font-bold">Coefficient C: {selectedMaterial.value} ({selectedMaterial.range})</span>
        </div>
        <p className="text-slate-400 text-[11px] leading-relaxed">{selectedMaterial.description}</p>
        <div className="flex items-center gap-1 text-slate-400 text-[10px]">
          <ShieldCheck className="w-3 h-3 text-sky-400 flex-shrink-0" />
          <span>Source: {selectedMaterial.source}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Number of Downpipes
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={data.num_downpipes || 1}
            onChange={(e) => onChange({ num_downpipes: parseInt(e.target.value, 10) || 1 })}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 font-mono focus:border-sky-500"
          />
        </div>

        <div className="flex items-center pt-5">
          <label className="flex items-center gap-2.5 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={data.has_first_flush_diverter ?? true}
              onChange={(e) => onChange({ has_first_flush_diverter: e.target.checked })}
              className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-sky-500"
            />
            <span>First-Flush Diverter Installed / Planned (IS 15797:2008)</span>
          </label>
        </div>
      </div>
    </div>
  );
};
