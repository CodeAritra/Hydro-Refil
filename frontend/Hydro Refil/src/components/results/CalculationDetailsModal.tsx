import React, { useState } from 'react';
import { Calculator, X, ChevronDown, ChevronRight, CheckCircle2, ShieldAlert } from 'lucide-react';
import { CalculationTraceItem } from '../../types';

interface CalculationDetailsModalProps {
  traces: CalculationTraceItem[];
  isOpen: boolean;
  onClose: () => void;
}

export const CalculationDetailsModal: React.FC<CalculationDetailsModalProps> = ({
  traces,
  isOpen,
  onClose,
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/20 text-sky-400">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Hydrological Calculation Audit Trail</h3>
              <p className="text-xs text-slate-400">Step-by-step formula substitutions, engineering units & source citations</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content list */}
        <div className="p-5 overflow-y-auto space-y-3 flex-1">
          {traces.map((trace, idx) => {
            const isExpanded = expandedIndex === idx;
            return (
              <div
                key={idx}
                className="border border-slate-800 rounded-xl overflow-hidden bg-slate-800/40 hover:border-slate-700 transition-colors"
              >
                <button
                  type="button"
                  onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                  className="w-full p-4 text-left flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 text-xs font-mono font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <div>
                      <h4 className="text-sm font-semibold text-white">{trace.formula_name}</h4>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">{trace.formula_expression}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-slate-800 text-sky-300 border border-slate-700">
                      {trace.result}
                    </span>
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 pt-2 border-t border-slate-800/80 bg-slate-900/50 space-y-3 text-xs">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                        Substituted Input Variables
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {Object.entries(trace.inputs).map(([k, v]) => (
                          <div key={k} className="bg-slate-800/80 p-2 rounded border border-slate-700/60 flex justify-between">
                            <span className="text-slate-400">{k}:</span>
                            <span className="text-slate-200 font-mono font-medium">{v}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {trace.notes && (
                      <div className="bg-sky-950/40 border border-sky-800/40 p-2.5 rounded-lg text-sky-300 flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <span>{trace.notes}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex items-center justify-between text-xs text-slate-400">
          <span>All formulas compliant with IS 15797:2008 & CGWB methodology.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors"
          >
            Close Audit
          </button>
        </div>
      </div>
    </div>
  );
};
