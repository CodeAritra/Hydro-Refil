import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ListFilter, Search, PlusCircle, ArrowRight, Trash2, Calendar, MapPin, Droplets } from 'lucide-react';
import { assessmentService } from '../services/api';
import { AssessmentListItem } from '../types';

export const AssessmentList: React.FC = () => {
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      try {
        const list = await assessmentService.listAssessments();
        setAssessments(list);
      } catch (err) {
        console.error('Failed to load assessment list:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete assessment for "${name}"?`)) return;
    try {
      await assessmentService.deleteAssessment(id);
      setAssessments((prev) => prev.filter((a) => a.id !== id));
    } catch (e) {
      alert('Delete failed.');
    }
  };

  const filtered = assessments.filter(
    (a) =>
      a.site_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.location_summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.recommended_structure.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Top Title & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
            Evaluation Archive
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Historical Field Assessments
          </h1>
        </div>

        <Link
          to="/assessment/new"
          className="flex items-center gap-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md shadow-sky-500/25 transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Assessment</span>
        </Link>
      </div>

      {/* Search Filter Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Filter by site name, district, state or recommended structure..."
          className="w-full bg-slate-800/80 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-400 focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
        />
      </div>

      {/* Table / List Container */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800">
        {loading ? (
          <div className="py-12 text-center text-slate-400 text-sm animate-pulse">
            Loading assessment logs...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm space-y-2">
            <p>No matching assessment records found.</p>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="text-sky-400 hover:underline text-xs font-semibold"
              >
                Clear Search Filter
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700/60">
                <tr>
                  <th className="py-3 px-4 rounded-l-lg">Site Identification</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Roof Catchment</th>
                  <th className="py-3 px-4">Annual Harvest</th>
                  <th className="py-3 px-4">Recommendation</th>
                  <th className="py-3 px-4 rounded-r-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      <Link to={`/assessment/${item.id}`} className="hover:text-sky-400 font-bold block">
                        {item.site_name}
                      </Link>
                      <span className="text-[10px] text-slate-500 font-normal">
                        Assessor: {item.assessor_name || 'Field Engineer'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{item.location_summary}</td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-medium">{item.roof_area_m2} m²</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-sky-400">
                      {item.annual_harvestable_m3} m³
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium">
                        {item.recommended_structure}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <Link
                        to={`/assessment/${item.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 font-medium text-xs border border-sky-500/30 transition-all"
                      >
                        <span>View</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                      <button
                        onClick={() => handleDelete(item.id, item.site_name)}
                        className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        title="Delete Record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
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
