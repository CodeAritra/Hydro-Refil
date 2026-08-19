import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { MonthlyDataPoint } from '../../types';

interface MonthlyRunoffChartProps {
  data: MonthlyDataPoint[];
}

export const MonthlyRunoffChart: React.FC<MonthlyRunoffChartProps> = ({ data }) => {
  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis dataKey="month" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis
            yAxisId="left"
            stroke="#94a3b8"
            tick={{ fontSize: 11 }}
            tickFormatter={(val) => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#38bdf8"
            tick={{ fontSize: 11 }}
            tickFormatter={(val) => `${val} mm`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              borderColor: '#475569',
              borderRadius: '0.5rem',
              color: '#f8fafc',
              fontSize: '12px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
            }}
            formatter={(value: any, name: string) => {
              if (name === 'Rainfall') return [`${value} mm`, name];
              return [`${Number(value).toLocaleString()} Litres`, name];
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
          {/* Rainfall Line */}
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="rainfall_mm"
            name="Rainfall"
            stroke="#38bdf8"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#38bdf8' }}
          />
          {/* Net Harvestable Bar */}
          <Bar
            yAxisId="left"
            dataKey="net_harvestable_litres"
            name="Harvestable Runoff"
            fill="#0284c7"
            radius={[4, 4, 0, 0]}
          />
          {/* Demand Line */}
          <Line
            yAxisId="left"
            type="step"
            dataKey="demand_litres"
            name="Monthly Demand"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
