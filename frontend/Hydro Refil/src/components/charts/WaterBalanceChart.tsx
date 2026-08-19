import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

interface WaterBalanceChartProps {
  harvestableLitres: number;
  demandLitres: number;
  rechargeLitres: number;
}

export const WaterBalanceChart: React.FC<WaterBalanceChartProps> = ({
  harvestableLitres,
  demandLitres,
  rechargeLitres,
}) => {
  const data = [
    { name: 'Harvest Potential', value: harvestableLitres / 1000, color: '#0284c7', unit: 'm³' },
    { name: 'Water Demand', value: demandLitres / 1000, color: '#f59e0b', unit: 'm³' },
    { name: 'Recharge Potential', value: rechargeLitres / 1000, color: '#0d9488', unit: 'm³' },
  ];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <YAxis
            stroke="#94a3b8"
            tick={{ fontSize: 11 }}
            tickFormatter={(val) => `${val} m³`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              borderColor: '#475569',
              borderRadius: '0.5rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
            formatter={(value: any) => [`${Number(value).toFixed(2)} m³ (${(Number(value) * 1000).toLocaleString()} L)`, 'Annual Volume']}
          />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
