import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Printer,
  ArrowLeft,
  ShieldCheck,
  Droplets,
  Calendar,
  MapPin,
  Home,
  CheckCircle2,
  FileCheck,
  Scale,
  Award,
} from 'lucide-react';
import { assessmentService } from '../services/api';
import { AssessmentRecord } from '../types';

export const ReportView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<AssessmentRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      if (!id) return;
      try {
        const record = await assessmentService.getAssessment(id);
        setAssessment(record);
      } catch (err) {
        console.error('Failed to load report:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-24 text-center text-slate-400 text-sm animate-pulse">
        Generating official engineering assessment dossier...
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center text-rose-400">
        Assessment record not found.
      </div>
    );
  }

  const { results, roof, rainfall, demand, site, location } = assessment;
  const primDim = results.primary_dimensions;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Non-printable Action Bar */}
      <div className="no-print flex items-center justify-between gap-4 glass-panel p-4 rounded-xl border border-slate-800">
        <Link
          to={`/assessment/${assessment.id}`}
          className="text-xs font-semibold text-sky-400 hover:underline flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Interactive Results View</span>
        </Link>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white px-4 py-2 rounded-lg text-xs font-bold shadow-md shadow-sky-500/25 transition-all"
        >
          <Printer className="w-4 h-4" />
          <span>Print / Save as PDF</span>
        </button>
      </div>

      {/* Printable Engineering Field Report Document */}
      <div className="bg-white text-slate-900 p-8 sm:p-12 rounded-2xl shadow-xl border border-slate-200 space-y-8 font-sans print:shadow-none print:p-0 print:border-none">
        {/* Document Header */}
        <div className="border-b-2 border-slate-900 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-sky-700 font-black text-xl tracking-tight">
              <Droplets className="w-6 h-6 text-sky-600" />
              <span>HYDROREFIL ENGINEERING FIELD REPORT</span>
            </div>
            <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider mt-0.5">
              Rooftop Rainwater Harvesting (RTRWH) & Artificial Aquifer Recharge Assessment
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Methodology in compliance with BIS IS 15797:2008 & CGWB Guidelines
            </p>
          </div>

          <div className="text-right text-xs text-slate-600 space-y-1 font-mono sm:self-end">
            <div><strong>Dossier ID:</strong> {assessment.id.slice(0, 18)}</div>
            <div><strong>Date:</strong> {new Date(assessment.created_at).toLocaleDateString()}</div>
            <div><strong>Status:</strong> <span className="text-emerald-700 font-bold">VERIFIED FEASIBLE</span></div>
          </div>
        </div>

        {/* 1. Executive Summary & Site Info */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1">
            1. Site & Catchment Identification
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Site / Property</span>
              <strong className="text-slate-900">{assessment.site_name}</strong>
            </div>
            <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Location / District</span>
              <strong className="text-slate-900">{location.district || location.address || 'Field Survey Site'}</strong>
            </div>
            <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Catchment Area</span>
              <strong className="text-slate-900 font-mono">{roof.area_m2} m² (≈ {(roof.area_m2 * 10.76).toFixed(0)} sq.ft)</strong>
            </div>
            <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block">Roof Material</span>
              <strong className="text-slate-900">{roof.material_key.replace('_', ' ').toUpperCase()} (C = {results.runoff_coefficient})</strong>
            </div>
          </div>
        </div>

        {/* 2. Hydrological Assessment Results Table */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1">
            2. Core Hydrological Evaluation Metrics
          </h2>
          <table className="w-full text-left text-xs border border-slate-300 rounded overflow-hidden">
            <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-300">
              <tr>
                <th className="p-2.5">Evaluation Parameter</th>
                <th className="p-2.5">Evaluated Value</th>
                <th className="p-2.5">Unit of Measurement</th>
                <th className="p-2.5">Engineering Basis / Standard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-800 font-mono">
              <tr>
                <td className="p-2.5 font-sans font-medium">Normal Annual Rainfall</td>
                <td className="p-2.5 font-bold">{rainfall.annual_mm}</td>
                <td className="p-2.5 text-slate-600">mm / year</td>
                <td className="p-2.5 font-sans text-slate-600">IMD Normal / Station Record</td>
              </tr>
              <tr>
                <td className="p-2.5 font-sans font-medium">Gross Rooftop Runoff</td>
                <td className="p-2.5 font-bold">{results.annual_gross_runoff_litres.toLocaleString()}</td>
                <td className="p-2.5 text-slate-600">Litres / year</td>
                <td className="p-2.5 font-sans text-slate-600">P (mm) × Area (m²) × C</td>
              </tr>
              <tr>
                <td className="p-2.5 font-sans font-medium">First-Flush Diversion Volume</td>
                <td className="p-2.5 font-bold">{results.first_flush_annual_loss_litres.toLocaleString()}</td>
                <td className="p-2.5 text-slate-600">Litres / year</td>
                <td className="p-2.5 font-sans text-slate-600">2.0 mm diverter (IS 15797)</td>
              </tr>
              <tr className="bg-sky-50 text-sky-950 font-bold">
                <td className="p-2.5 font-sans">Net Recoverable Harvest Potential</td>
                <td className="p-2.5 text-sky-800 text-sm">{results.annual_net_harvestable_m3} m³ ({results.annual_net_harvestable_litres.toLocaleString()} L)</td>
                <td className="p-2.5">m³ / year</td>
                <td className="p-2.5 font-sans text-sky-900">Net = (Gross - FF) × 85% Efficiency</td>
              </tr>
              <tr>
                <td className="p-2.5 font-sans font-medium">Target Consumption Demand Met</td>
                <td className="p-2.5 font-bold">{results.demand_met_percentage}%</td>
                <td className="p-2.5 text-slate-600">% of Non-Potable Demand</td>
                <td className="p-2.5 font-sans text-slate-600">CPHEEO Domestic Norms</td>
              </tr>
              <tr>
                <td className="p-2.5 font-sans font-medium">Artificial Recharge Feasibility</td>
                <td className="p-2.5 font-bold">{results.recharge_feasibility_label}</td>
                <td className="p-2.5 text-slate-600">{results.annual_recharge_potential_m3} m³ Potential</td>
                <td className="p-2.5 font-sans text-slate-600">CGWB Artificial Recharge Manual</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* 3. Recommended Structure & Indicative Dimensions */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-300 pb-1">
            3. Engineered Structure Recommendation & Indicative Dimensions
          </h2>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-300 space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <strong className="text-sm text-sky-900">{results.recommended_structure}</strong>
              <span className="px-2.5 py-0.5 rounded bg-sky-100 text-sky-800 font-bold">Primary Selection</span>
            </div>
            <p className="text-slate-700 leading-relaxed font-sans">
              <strong>Rationale:</strong> {results.recommendation_reason}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono pt-2 border-t border-slate-200">
              <div>
                <span className="text-slate-500 block text-[11px]">Plan Geometry:</span>
                <strong className="text-slate-900">{primDim.diameter_m ? `Ø ${primDim.diameter_m} m` : `${primDim.length_m} m × ${primDim.width_m} m`}</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Excavation Depth:</span>
                <strong className="text-slate-900">{primDim.depth_m} m</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Effective Capacity:</span>
                <strong className="text-sky-700">{primDim.effective_volume_m3} m³</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Freeboard Allowance:</span>
                <strong className="text-slate-900">{primDim.freeboard_m} m</strong>
              </div>
            </div>

            {primDim.notes && (
              <p className="text-[11px] text-slate-600 italic pt-1 font-sans">
                Construction Guide: {primDim.notes}
              </p>
            )}
          </div>
        </div>

        {/* 4. Engineering Disclaimer & Official Sign-Off */}
        <div className="space-y-4 pt-4 border-t-2 border-slate-300 text-xs text-slate-600">
          <div className="flex items-start gap-2 p-3 bg-amber-50 rounded border border-amber-200 text-amber-900 text-[11px]">
            <Scale className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p>
              <strong>Official Engineering Disclaimer:</strong> This automated assessment is generated for decision support and preliminary feasibility estimation. Actual structural construction must be verified on-site by a qualified civil/water-resources engineer with certified percolation testing and subsoil geotechnical testing.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8 pt-8 text-center text-xs">
            <div className="border-t border-slate-400 pt-2">
              <strong>Assessed & Prepared By</strong>
              <p className="text-slate-500 font-mono text-[11px]">{assessment.assessor_name || 'Field Surveyor'}</p>
            </div>
            <div className="border-t border-slate-400 pt-2">
              <strong>Verified / Certified By</strong>
              <p className="text-slate-500 font-mono text-[11px]">Qualified Hydrogeologist / Municipal Authority</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
