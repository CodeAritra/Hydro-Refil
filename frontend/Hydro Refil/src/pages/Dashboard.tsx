import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Droplets,
  PlusCircle,
  BarChart3,
  Waves,
  MapPin,
  Calendar,
  ArrowRight,
  ShieldCheck,
  Zap,
  BookOpen,
  Sparkles,
} from 'lucide-react';
import { assessmentService } from '../services/api';
import { AssessmentListItem } from '../types';
import { MetricCard } from '../components/results/MetricCard';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const list = await assessmentService.listAssessments();
        setAssessments(list);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalHarvestM3 = assessments.reduce((acc, curr) => acc + (curr.annual_harvestable_m3 || 0), 0);
  const totalRoofArea = assessments.reduce((acc, curr) => acc + (curr.roof_area_m2 || 0), 0);

  const handleLaunchDemoScenario = async () => {
    try {
      const demoPayload = {
        site_name: 'SIH Demo — National Institute of Hydrology Campus',
        assessor_name: 'Dr. S. K. Verma (Senior Hydrologist)',
        organization: 'Smart India Hackathon Technical Committee',
        remarks: 'Institutional demonstration site evaluated for rooftop rainwater harvesting and artificial aquifer recharge.',
        location: {
          latitude: 28.6139,
          longitude: 77.2090,
          district: 'New Delhi',
          state: 'Delhi',
          address: 'Central Institutional Area, New Delhi',
        },
        roof: {
          area_m2: 850.0,
          material_key: 'rcc_concrete' as const,
          slope_deg: 0,
          num_downpipes: 6,
          has_first_flush_diverter: true,
        },
        rainfall: {
          annual_mm: 790.0,
          data_source: 'imd_database',
        },
        demand: {
          num_people: 45,
          per_capita_demand_lpd: 45.0,
          non_potable_fraction: 0.50,
        },
        site: {
          soil_type_key: 'sandy_loam' as const,
          groundwater_depth_mbgl: 14.5,
          available_area_m2: 40.0,
        },
      };

      const record = await assessmentService.createAssessment(demoPayload);
      navigate(`/assessment/${record.id}`);
    } catch (e) {
      console.error('Failed to launch demo scenario:', e);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel border border-sky-500/30 p-6 sm:p-10 bg-gradient-to-r from-slate-900 via-slate-900/90 to-sky-950/40">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Smart India Hackathon Decision Support System</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
            Rapid On-Spot <span className="hydro-gradient-text">RTRWH & Recharge</span> Sizing Platform
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Conduct rapid field-level engineering assessments of rooftop rainwater harvesting potential, water balance, and subsoil artificial groundwater recharge structures with complete mathematical traceability and CGWB/BIS standard compliance.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              to="/assessment/new"
              className="flex items-center gap-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-lg shadow-sky-500/25 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New Site Assessment</span>
            </Link>

            <button
              onClick={handleLaunchDemoScenario}
              className="flex items-center gap-2 bg-slate-800/90 hover:bg-slate-750 text-sky-300 hover:text-white px-5 py-2.5 rounded-xl font-semibold text-sm border border-slate-700 hover:border-sky-500/40 transition-all"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Load 1-Click SIH Demo Site</span>
            </button>
          </div>
        </div>
      </div>

      {/* Aggregate KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Evaluated Sites"
          value={assessments.length}
          unit="Records"
          subtext="Saved field assessments"
          icon={BarChart3}
          variant="sky"
        />
        <MetricCard
          title="Harvestable Potential"
          value={totalHarvestM3.toFixed(1)}
          unit="m³ / year"
          subtext={`≈ ${(totalHarvestM3 * 1000).toLocaleString()} Litres`}
          icon={Droplets}
          variant="emerald"
        />
        <MetricCard
          title="Catchment Assessed"
          value={totalRoofArea.toFixed(0)}
          unit="m² Total"
          subtext={`Across ${assessments.length} building rooftops`}
          icon={MapPin}
          variant="indigo"
        />
        <MetricCard
          title="Engineering Compliance"
          value="100%"
          unit="IS 15797:2008"
          subtext="CGWB standard formulas"
          icon={ShieldCheck}
          variant="amber"
        />
      </div>

      {/* Recent Assessments Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-sky-400" />
              Recent Field Assessments
            </h2>
            <p className="text-xs text-slate-400">Review, inspect, or export full hydrological engineering dossiers</p>
          </div>
          <Link
            to="/assessments"
            className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center gap-1 transition-colors"
          >
            <span>View All ({assessments.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 text-sm animate-pulse">
            Loading assessment records...
          </div>
        ) : assessments.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm space-y-3">
            <p>No site assessments found yet.</p>
            <button
              onClick={handleLaunchDemoScenario}
              className="text-sky-400 hover:underline text-xs font-semibold"
            >
              Click here to load the sample SIH evaluation scenario
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700/60">
                <tr>
                  <th className="py-3 px-4 rounded-l-lg">Site Name</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Roof Area</th>
                  <th className="py-3 px-4">Annual Harvest</th>
                  <th className="py-3 px-4">Recommended Structure</th>
                  <th className="py-3 px-4 rounded-r-lg text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {assessments.slice(0, 5).map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      <Link to={`/assessment/${item.id}`} className="hover:text-sky-400">
                        {item.site_name}
                      </Link>
                      <span className="block text-[10px] text-slate-500 font-normal">
                        Assessed by: {item.assessor_name || 'Field Engineer'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{item.location_summary}</td>
                    <td className="py-3.5 px-4 font-mono font-medium">{item.roof_area_m2} m²</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-sky-400">
                      {item.annual_harvestable_m3} m³
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-1 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium">
                        {item.recommended_structure}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        to={`/assessment/${item.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-medium text-xs border border-sky-500/30 transition-all"
                      >
                        <span>View Results</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
