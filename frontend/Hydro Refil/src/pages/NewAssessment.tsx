import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  MapPin,
  Home,
  CloudRain,
  Users,
  Shovel,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  Calculator,
  Droplets,
  Box,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { assessmentService } from '../services/api';
import { LocationPicker } from '../components/map/LocationPicker';
import { SiteInfoForm } from '../components/forms/SiteInfoForm';
import { RoofForm } from '../components/forms/RoofForm';
import { RainfallForm } from '../components/forms/RainfallForm';
import { DemandForm } from '../components/forms/DemandForm';
import { SiteConditionsForm } from '../components/forms/SiteConditionsForm';
import { calculateRTRWHOffline } from '../domain/hydrology';
import { RoofInput, RainfallInput, WaterDemandInput, SiteConditionsInput, LocationInput } from '../types';

export const NewAssessment: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [saving, setSaving] = useState<boolean>(false);

  // Form State
  const [siteInfo, setSiteInfo] = useState({
    site_name: '',
    assessor_name: 'Field Engineer',
    organization: '',
    remarks: '',
  });

  const [location, setLocation] = useState<LocationInput>({
    latitude: 22.5726,
    longitude: 88.3639,
    address: 'Survey Point Alpha',
    district: 'Kolkata',
    state: 'West Bengal',
  });

  const [roof, setRoof] = useState<RoofInput>({
    area_m2: 250,
    material_key: 'rcc_concrete',
    slope_deg: 0,
    num_downpipes: 2,
    has_first_flush_diverter: true,
  });

  const [rainfall, setRainfall] = useState<RainfallInput>({
    annual_mm: 1600,
    data_source: 'imd_database',
  });

  const [demand, setDemand] = useState<WaterDemandInput>({
    num_people: 6,
    per_capita_demand_lpd: 135,
    occupancy_type: 'domestic_urban',
    non_potable_fraction: 0.40,
  });

  const [siteConditions, setSiteConditions] = useState<SiteConditionsInput>({
    soil_type_key: 'sandy_loam',
    groundwater_depth_mbgl: 12.0,
    available_area_m2: 30.0,
  });

  // Real-time live calculation preview
  const liveResults = useMemo(() => {
    return calculateRTRWHOffline(roof, rainfall, demand, siteConditions);
  }, [roof, rainfall, demand, siteConditions]);

  const steps = [
    { id: 1, label: 'Site Info', icon: Building2 },
    { id: 2, label: 'Location / Map', icon: MapPin },
    { id: 3, label: 'Roof Catchment', icon: Home },
    { id: 4, label: 'Rainfall', icon: CloudRain },
    { id: 5, label: 'Water Demand', icon: Users },
    { id: 6, label: 'Soil & Aquifer', icon: Shovel },
  ];

  const handleNext = () => {
    if (currentStep === 1 && !siteInfo.site_name.trim()) {
      alert('Please enter a site or building name to proceed.');
      return;
    }
    if (currentStep < 6) setCurrentStep(currentStep + 1);
  };

  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteInfo.site_name.trim()) {
      alert('Please enter a site name.');
      return;
    }

    setSaving(true);
    try {
      const record = await assessmentService.createAssessment({
        site_name: siteInfo.site_name,
        assessor_name: siteInfo.assessor_name,
        organization: siteInfo.organization,
        remarks: siteInfo.remarks,
        location,
        roof,
        rainfall,
        demand,
        site: siteConditions,
      });
      navigate(`/assessment/${record.id}`);
    } catch (err) {
      console.error('Failed to create assessment:', err);
      alert('Failed to save assessment. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
            Field Evaluation Wizard
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            On-Spot RTRWH Assessment
          </h1>
        </div>

        {/* Step indicators */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          {steps.map((step) => {
            const Icon = step.icon;
            const isDone = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <button
                key={step.id}
                type="button"
                onClick={() => setCurrentStep(step.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  isCurrent
                    ? 'bg-sky-500 text-white shadow-md shadow-sky-500/30'
                    : isDone
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{step.label}</span>
                <span className="sm:hidden">{step.id}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Form wizard on left, Live computation dock on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Form Container */}
        <div className="lg:col-span-2 glass-card p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1 */}
            {currentStep === 1 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-sky-400" />
                    Step 1: Site Metadata & Assessor Information
                  </h3>
                  <p className="text-xs text-slate-400">Specify property identification details</p>
                </div>
                <SiteInfoForm
                  data={siteInfo}
                  onChange={(fields) => setSiteInfo((prev) => ({ ...prev, ...fields }))}
                />
              </div>
            )}

            {/* Step 2 */}
            {currentStep === 2 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-sky-400" />
                    Step 2: Geographic Location & Map Selection
                  </h3>
                  <p className="text-xs text-slate-400">Pin site coordinates or choose an Indian district preset</p>
                </div>
                <LocationPicker
                  latitude={location.latitude || 22.5726}
                  longitude={location.longitude || 88.3639}
                  address={location.address}
                  district={location.district}
                  state={location.state}
                  onChange={(loc) => {
                    setLocation((prev) => ({ ...prev, ...loc }));
                    if (loc.rainfall_mm) {
                      setRainfall((prev) => ({ ...prev, annual_mm: loc.rainfall_mm!, data_source: 'imd_database' }));
                    }
                  }}
                />
              </div>
            )}

            {/* Step 3 */}
            {currentStep === 3 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Home className="w-4 h-4 text-sky-400" />
                    Step 3: Roof Catchment & Material Properties
                  </h3>
                  <p className="text-xs text-slate-400">Configure effective surface area and standard runoff coefficient</p>
                </div>
                <RoofForm
                  data={roof}
                  onChange={(fields) => setRoof((prev) => ({ ...prev, ...fields }))}
                />
              </div>
            )}

            {/* Step 4 */}
            {currentStep === 4 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <CloudRain className="w-4 h-4 text-sky-400" />
                    Step 4: Rainfall Availability
                  </h3>
                  <p className="text-xs text-slate-400">Enter normal annual rainfall or verify district meteorological normal</p>
                </div>
                <RainfallForm
                  data={rainfall}
                  onChange={(fields) => setRainfall((prev) => ({ ...prev, ...fields }))}
                />
              </div>
            )}

            {/* Step 5 */}
            {currentStep === 5 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Users className="w-4 h-4 text-sky-400" />
                    Step 5: Water Demand & Consumption Standard
                  </h3>
                  <p className="text-xs text-slate-400">Quantify user consumption and target non-potable rainwater replacement</p>
                </div>
                <DemandForm
                  data={demand}
                  onChange={(fields) => setDemand((prev) => ({ ...prev, ...fields }))}
                />
              </div>
            )}

            {/* Step 6 */}
            {currentStep === 6 && (
              <div className="space-y-4 animate-fade-in">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Shovel className="w-4 h-4 text-sky-400" />
                    Step 6: Subsoil Permeability & Hydrogeological Constraints
                  </h3>
                  <p className="text-xs text-slate-400">Assess groundwater depth and infiltration feasibility</p>
                </div>
                <SiteConditionsForm
                  data={siteConditions}
                  onChange={(fields) => setSiteConditions((prev) => ({ ...prev, ...fields }))}
                />
              </div>
            )}

            {/* Navigation buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  currentStep === 1
                    ? 'opacity-40 cursor-not-allowed text-slate-500'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                }`}
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              {currentStep < 6 ? (
                <button
                  type="button"
                  onClick={handleNext}
                  className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white rounded-lg text-sm font-bold shadow-md shadow-sky-500/25 transition-all"
                >
                  <span>Next Step</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-2 px-8 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white rounded-lg text-sm font-bold shadow-lg shadow-emerald-500/30 transition-all"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{saving ? 'Finalizing Dossier...' : 'Execute Assessment & Save'}</span>
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Live Calculation Preview Dock */}
        <div className="glass-panel p-6 rounded-2xl border border-sky-500/30 space-y-5 bg-gradient-to-b from-slate-900 to-slate-950 sticky top-24">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 text-sky-400 font-bold text-sm">
              <Calculator className="w-4 h-4" />
              <span>Real-Time Calculation Dock</span>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/40 animate-pulse">
              LIVE
            </span>
          </div>

          {/* Annual Potential */}
          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-medium block">Net Annual Harvest Yield</span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-sky-400 font-mono">
                {liveResults.annual_net_harvestable_m3}
              </span>
              <span className="text-sm font-semibold text-slate-300">m³ / yr</span>
            </div>
            <span className="text-xs text-slate-400">
              ≈ {liveResults.annual_net_harvestable_litres.toLocaleString()} Litres
            </span>
          </div>

          {/* Structure Recommendation */}
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-1.5">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block flex items-center gap-1.5">
              <Box className="w-3.5 h-3.5 text-teal-400" />
              Recommended Structure
            </span>
            <span className="text-sm font-bold text-white block">
              {liveResults.recommended_structure}
            </span>
            <span className="text-xs text-slate-300 font-mono block">
              Indicative Dimensions: {liveResults.primary_dimensions.dimension_string}
            </span>
          </div>

          {/* Water Demand Balance */}
          {demand.num_people > 0 && (
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-slate-300">
                <span>Target Demand Met:</span>
                <span className="font-mono font-bold text-emerald-400">
                  {liveResults.demand_met_percentage}%
                </span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-sky-500 to-emerald-400 transition-all duration-300"
                  style={{ width: `${Math.min(100, liveResults.demand_met_percentage)}%` }}
                />
              </div>
            </div>
          )}

          {/* Feasibility Indicator */}
          <div className="flex items-center justify-between text-xs pt-1">
            <span className="text-slate-400">Feasibility Status:</span>
            <span className="font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              {liveResults.feasibility_label}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
