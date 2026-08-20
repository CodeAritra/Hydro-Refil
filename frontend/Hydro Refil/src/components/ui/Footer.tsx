import React from 'react';
import { Droplet, ShieldCheck, Scale, Award } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950/80 mt-auto text-slate-400 text-xs no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <Droplet className="w-4 h-4 text-sky-400" />
              <span>HydroRefil — RTRWH Decision Support Engine</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-lg">
              Engineered for on-spot rooftop rainwater harvesting assessment, groundwater recharge feasibility, and structure sizing in compliance with Central Ground Water Board (CGWB) and Bureau of Indian Standards (BIS IS 15797:2008).
            </p>
            <div className="flex items-center gap-2 text-amber-400/90 text-[11px] bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-md max-w-lg">
              <Scale className="w-4 h-4 flex-shrink-0" />
              <span>Indicative preliminary estimation. Field verification required before structural construction.</span>
            </div>
          </div>

          <div>
            <h4 className="text-slate-200 font-semibold mb-3 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
              Standard References
            </h4>
            <ul className="space-y-1.5 text-slate-400">
              <li>• CGWB Master Plan (2005/2013)</li>
              <li>• BIS IS 15797:2008 (RTRWH Code)</li>
              <li>• CPHEEO Water Supply Manual</li>
              <li>• Jal Jeevan Mission & Jal Shakti Guidelines</li>
            </ul>
          </div>

          <div>
            <h4 className="text-slate-200 font-semibold mb-3 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-sky-400" />
              HydroRefil Solution
            </h4>
            <p className="text-slate-400 mb-2">
              Problem: Rapid on-spot RTRWH & Artificial Recharge potential evaluation & sizing.
            </p>
            <p className="text-slate-500 text-[11px]">
              Offline-capable • Unit-traceable • Deterministic
            </p>
          </div>
        </div>

        <div className="border-t border-slate-800/80 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500">
          <p>© {new Date().getFullYear()} HydroRefil Platform. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Engine Online & Offline Ready
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
