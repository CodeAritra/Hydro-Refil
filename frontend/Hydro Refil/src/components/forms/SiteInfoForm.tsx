import React from 'react';
import { Building2, User, Building, FileText } from 'lucide-react';

interface SiteInfoFormProps {
  data: {
    site_name: string;
    assessor_name?: string;
    organization?: string;
    remarks?: string;
  };
  onChange: (fields: Partial<SiteInfoFormProps['data']>) => void;
}

export const SiteInfoForm: React.FC<SiteInfoFormProps> = ({ data, onChange }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
          <Building2 className="w-3.5 h-3.5 text-sky-400" />
          Site / Building Name *
        </label>
        <input
          type="text"
          required
          value={data.site_name}
          onChange={(e) => onChange({ site_name: e.target.value })}
          placeholder="e.g. Kendriya Vidyalaya Campus, Block A"
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-slate-400" />
            Field Assessor Name
          </label>
          <input
            type="text"
            value={data.assessor_name || ''}
            onChange={(e) => onChange({ assessor_name: e.target.value })}
            placeholder="e.g. Er. Rajesh Kumar"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-sky-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
            <Building className="w-3.5 h-3.5 text-slate-400" />
            Agency / Institution
          </label>
          <input
            type="text"
            value={data.organization || ''}
            onChange={(e) => onChange({ organization: e.target.value })}
            placeholder="e.g. State Groundwater Dept / Municipal Corp"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-sky-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-slate-400" />
          Field Remarks / Site Notes
        </label>
        <textarea
          rows={2}
          value={data.remarks || ''}
          onChange={(e) => onChange({ remarks: e.target.value })}
          placeholder="e.g. Flat RCC roof with 4 existing downpipes; open garden space available on east boundary."
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-sky-500"
        />
      </div>
    </div>
  );
};
