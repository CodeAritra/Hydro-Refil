import React from 'react';
import { Box, Layers, ShieldCheck, Ruler, Info } from 'lucide-react';
import { StructureDimensions } from '../../types';

interface StructureCardProps {
  structureName: string;
  reason: string;
  dimensions: StructureDimensions;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  isSecondary?: boolean;
}

export const StructureCard: React.FC<StructureCardProps> = ({
  structureName,
  reason,
  dimensions,
  confidence,
  isSecondary = false,
}) => {
  const confidenceStyles = {
    HIGH: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    MEDIUM: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    LOW: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  };

  return (
    <div
      className={`p-5 rounded-xl border glass-card transition-all ${
        isSecondary
          ? 'border-slate-700/80 bg-slate-800/40'
          : 'border-sky-500/40 bg-gradient-to-br from-slate-900 via-slate-800/80 to-slate-900'
      }`}
    >
      {/* Title & Badge */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-lg ${isSecondary ? 'bg-slate-700/50 text-slate-300' : 'bg-sky-500/20 text-sky-400'}`}>
            <Box className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">
                {isSecondary ? 'Complementary Storage' : 'Recommended Primary Structure'}
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${confidenceStyles[confidence]}`}>
                {confidence} CONFIDENCE
              </span>
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white mt-0.5">{structureName}</h3>
          </div>
        </div>
      </div>

      {/* Rationale explanation */}
      <div className="bg-slate-800/70 p-3 rounded-lg border border-slate-700/60 mb-4 text-xs text-slate-300 leading-relaxed flex items-start gap-2">
        <Info className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-100 block mb-0.5">Engineering Justification:</strong>
          {reason}
        </div>
      </div>

      {/* Sizing Dimensions Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs mb-3">
        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block font-medium">Plan Geometry</span>
          <span className="text-white font-mono font-semibold text-sm">
            {dimensions.diameter_m
              ? `Ø ${dimensions.diameter_m} m`
              : `${dimensions.length_m || '-'} m × ${dimensions.width_m || '-'} m`}
          </span>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block font-medium">Design Depth</span>
          <span className="text-white font-mono font-semibold text-sm">
            {dimensions.depth_m ? `${dimensions.depth_m} m` : '-'}
          </span>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block font-medium">Effective Storage</span>
          <span className="text-sky-400 font-mono font-bold text-sm">
            {dimensions.effective_volume_m3 ? `${dimensions.effective_volume_m3} m³` : '-'}
          </span>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
          <span className="text-slate-400 block font-medium">Freeboard Allowance</span>
          <span className="text-white font-mono font-semibold text-sm">
            {dimensions.freeboard_m ? `${dimensions.freeboard_m} m` : '0.30 m'}
          </span>
        </div>
      </div>

      {/* Notes / Construction guide */}
      {dimensions.notes && (
        <p className="text-[11px] text-slate-400 italic bg-slate-900/50 px-3 py-1.5 rounded border border-slate-800/80">
          Note: {dimensions.notes}
        </p>
      )}
    </div>
  );
};
