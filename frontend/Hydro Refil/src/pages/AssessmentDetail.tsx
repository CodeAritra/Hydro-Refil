import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Calculator,
  Droplets,
  Calendar,
  MapPin,
  Home,
  Users,
  ShieldCheck,
  Printer,
  ArrowLeft,
  Trash2,
  CheckCircle2,
  Waves,
  PieChart,
  BarChart3,
} from 'lucide-react';
import { assessmentService } from '../services/api';
import { AssessmentRecord } from '../types';
import { MetricCard } from '../components/results/MetricCard';
import { StructureCard } from '../components/results/StructureCard';
import { WarningsAlert } from '../components/results/WarningsAlert';
import { CalculationDetailsModal } from '../components/results/CalculationDetailsModal';
import { MonthlyRunoffChart } from '../components/charts/MonthlyRunoffChart';
import { WaterBalanceChart } from '../components/charts/WaterBalanceChart';

export const AssessmentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<AssessmentRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCalcModal, setShowCalcModal] = useState<boolean>(false);

  useEffect(() => {
    async function fetchRecord() {
      if (!id) return;
      try {
        const data = await assessmentService.getAssessment(id);
        setAssessment(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load assessment dossier.');
      } finally {
        setLoading(false);
      }
    }
    fetchRecord();
  }, [id]);

  const handleDelete = async () => {
    if (!id || !confirm('Are you sure you want to delete this assessment record?')) return;
    try {
      await assessmentService.deleteAssessment(id);
      navigate('/assessments');
    } catch (err) {
      alert('Delete failed.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center text-slate-400 animate-pulse text-sm">
        Loading complete hydrological assessment results...
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <p className="text-rose-400 font-semibold">{error || 'Assessment not found.'}</p>
        <Link to="/" className="text-sky-400 hover:underline text-sm font-medium">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const { results, roof, rainfall, demand, site, location } = assessment;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Top Navigation & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <Link
            to="/assessments"
            className="text-xs font-semibold text-slate-400 hover:text-sky-400 flex items-center gap-1.5 mb-1.5 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to All Assessments</span>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
            <span>{assessment.site_name}</span>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30">
              {results.feasibility_label} FEASIBILITY
            </span>
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              {new Date(assessment.created_at).toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              {location.district ? `${location.district}, ${location.state || 'India'}` : (location.address || 'Geo-Location')}
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
              Assessor: {assessment.assessor_name || 'Field Engineer'}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={() => setShowCalcModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-sky-400 hover:text-sky-300 border border-slate-700 text-xs font-bold transition-all shadow-sm"
          >
            <Calculator className="w-4 h-4" />
            <span>Inspect Formulas</span>
          </button>

          <Link
            to={`/assessment/${assessment.id}/report`}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white text-xs font-bold shadow-md shadow-sky-500/20 transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Field Report</span>
          </Link>

          <button
            type="button"
            onClick={handleDelete}
            title="Delete Assessment"
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-800 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Net Harvest Potential"
          value={results.annual_net_harvestable_m3}
          unit="m³ / year"
          subtext={`≈ ${results.annual_net_harvestable_litres.toLocaleString()} Litres`}
          icon={Droplets}
          variant="sky"
        />
        <MetricCard
          title="Target Demand Met"
          value={`${results.demand_met_percentage}%`}
          unit="Harvestable Portion"
          subtext={`Demand: ${(results.annual_demand_litres / 1000).toFixed(1)} m³/yr`}
          icon={PieChart}
          variant={results.demand_met_percentage >= 50 ? 'emerald' : 'amber'}
        />
        <MetricCard
          title="Artificial Recharge"
          value={results.annual_recharge_potential_m3}
          unit="m³ / year"
          subtext={`Infiltration: ${results.infiltration_rate_mm_hr} mm/hr`}
          icon={Waves}
          variant="indigo"
        />
        <MetricCard
          title="Runoff Coefficient (C)"
          value={results.runoff_coefficient}
          unit="Dimensionless"
          subtext={`Efficiency: ${(results.system_efficiency * 100).toFixed(0)}% (CGWB)`}
          icon={Home}
          variant="amber"
        />
      </div>

      {/* Warnings & Constraints */}
      <WarningsAlert warnings={results.warnings} />

      {/* Recommended Sizing Structures */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              Engineered Structure Recommendations
            </h2>
            <p className="text-xs text-slate-400">Calculated indicative dimensions and civil design parameters</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StructureCard
            structureName={results.recommended_structure}
            reason={results.recommendation_reason}
            dimensions={results.primary_dimensions}
            confidence={results.confidence}
          />
          {results.secondary_dimensions && (
            <StructureCard
              structureName={results.secondary_structure || 'Supplementary Storage Tank'}
              reason="Supplementary storage component sized to fulfill dry-period consumption demand."
              dimensions={results.secondary_dimensions}
              confidence="MEDIUM"
              isSecondary={true}
            />
          )}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-sky-400" />
                Monthly Rainfall & Harvestable Runoff Hydrograph
              </h3>
              <p className="text-xs text-slate-400">Monthly water availability vs consumption demand (Litres & mm)</p>
            </div>
          </div>
          <MonthlyRunoffChart data={results.monthly_breakdown} />
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <PieChart className="w-4 h-4 text-teal-400" />
                Annual Water Balance (m³)
              </h3>
              <p className="text-xs text-slate-400">Harvest vs Demand vs Recharge</p>
            </div>
          </div>
          <WaterBalanceChart
            harvestableLitres={results.annual_net_harvestable_litres}
            demandLitres={results.annual_demand_litres}
            rechargeLitres={results.annual_recharge_potential_litres}
          />
        </div>
      </div>

      {/* Calculation Details Modal */}
      <CalculationDetailsModal
        isOpen={showCalcModal}
        onClose={() => setShowCalcModal(false)}
        traces={results.calculation_trace}
      />
    </div>
  );
};
