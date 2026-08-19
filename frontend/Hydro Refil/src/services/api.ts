/**
 * RTRWH Platform — API Service Layer
 * ===================================
 * Seamless API client with automatic offline fallback to the TypeScript domain engine.
 */

import axios from 'axios';
import {
  AssessmentRecord,
  AssessmentListItem,
  AssessmentCalculationResult,
  RoofInput,
  RainfallInput,
  WaterDemandInput,
  SiteConditionsInput,
  LocationInput,
} from '../types';
import { calculateRTRWHOffline } from '../domain/hydrology';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// LocalStorage Persistence Key for Offline Assessments
const STORAGE_KEY = 'hydrorefil_assessments_local';

function getLocalAssessments(): AssessmentRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveLocalAssessments(items: AssessmentRecord[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch (e) {
    console.error('LocalStorage write error:', e);
  }
}

export const assessmentService = {
  /**
   * Run quick assessment calculation (online or offline fallback).
   */
  async calculateHydrology(
    roof: RoofInput,
    rainfall: RainfallInput,
    demand?: WaterDemandInput,
    site?: SiteConditionsInput
  ): Promise<AssessmentCalculationResult> {
    try {
      const response = await client.post<AssessmentCalculationResult>('/api/hydrology/calculate', {
        roof,
        rainfall,
        demand,
        site,
      });
      return response.data;
    } catch (err) {
      console.warn('Backend API unavailable. Falling back to client-side offline hydrological engine:', err);
      // Run deterministic offline calculation
      return calculateRTRWHOffline(roof, rainfall, demand, site);
    }
  },

  /**
   * Create and persist a full site assessment record.
   */
  async createAssessment(payload: {
    site_name: string;
    assessor_name?: string;
    organization?: string;
    remarks?: string;
    location: LocationInput;
    roof: RoofInput;
    rainfall: RainfallInput;
    demand?: WaterDemandInput;
    site?: SiteConditionsInput;
  }): Promise<AssessmentRecord> {
    try {
      const response = await client.post<AssessmentRecord>('/api/assessments', payload);
      // Cache locally as well
      const local = getLocalAssessments();
      local.unshift(response.data);
      saveLocalAssessments(local);
      return response.data;
    } catch (err) {
      console.warn('Backend save failed. Saving to local storage for offline mode:', err);
      const results = calculateRTRWHOffline(payload.roof, payload.rainfall, payload.demand, payload.site);
      const newRecord: AssessmentRecord = {
        id: 'local-' + Date.now().toString(),
        site_name: payload.site_name,
        assessor_name: payload.assessor_name || 'Field Assessor',
        organization: payload.organization,
        remarks: payload.remarks,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        location: payload.location,
        roof: payload.roof,
        rainfall: payload.rainfall,
        demand: payload.demand || { num_people: 0, per_capita_demand_lpd: 135 },
        site: payload.site || { soil_type_key: 'unknown' },
        results,
      };

      const local = getLocalAssessments();
      local.unshift(newRecord);
      saveLocalAssessments(local);
      return newRecord;
    }
  },

  /**
   * List all assessments (merging server and local cache).
   */
  async listAssessments(): Promise<AssessmentListItem[]> {
    try {
      const response = await client.get<AssessmentListItem[]>('/api/assessments');
      if (response.data && response.data.length > 0) {
        return response.data;
      }
    } catch (err) {
      console.warn('Backend list failed. Loading locally saved assessments:', err);
    }

    const local = getLocalAssessments();
    return local.map((a) => ({
      id: a.id,
      site_name: a.site_name,
      assessor_name: a.assessor_name,
      created_at: a.created_at,
      location_summary: a.location.address || a.location.district || (a.location.latitude ? `${a.location.latitude.toFixed(3)}°N, ${a.location.longitude?.toFixed(3)}°E` : 'Local Assessment'),
      roof_area_m2: a.roof.area_m2,
      annual_harvestable_m3: a.results.annual_net_harvestable_m3,
      recommended_structure: a.results.recommended_structure,
      feasibility_label: a.results.feasibility_label,
    }));
  },

  /**
   * Retrieve a single assessment by ID.
   */
  async getAssessment(id: string): Promise<AssessmentRecord> {
    if (!id.startsWith('local-')) {
      try {
        const response = await client.get<AssessmentRecord>(`/api/assessments/${id}`);
        return response.data;
      } catch (err) {
        console.warn('Backend fetch failed. Checking local cache:', err);
      }
    }

    const local = getLocalAssessments();
    const found = local.find((a) => a.id === id);
    if (!found) {
      throw new Error(`Assessment ${id} not found in database or local storage.`);
    }
    return found;
  },

  /**
   * Delete assessment by ID.
   */
  async deleteAssessment(id: string): Promise<void> {
    if (!id.startsWith('local-')) {
      try {
        await client.delete(`/api/assessments/${id}`);
      } catch (err) {
        console.warn('Backend delete failed. Deleting locally:', err);
      }
    }
    const local = getLocalAssessments().filter((a) => a.id !== id);
    saveLocalAssessments(local);
  },
};
