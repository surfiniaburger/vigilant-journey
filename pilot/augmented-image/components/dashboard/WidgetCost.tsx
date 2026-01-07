
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { DashboardMetrics } from './useDatadogStream';

export function WidgetCost({ data }: { data: DashboardMetrics[] }) {
    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 h-64">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-400 text-sm font-medium">Estimated LLM Cost (Nano-USD)</h3>
                <span className="text-emerald-400 text-xs font-mono animate-pulse">● LIVE</span>
            </div>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={(ts) => new Date(ts).toLocaleTimeString([], { minute: '2-digit', second: '2-digit' })}
                        stroke="#52525b"
                        fontSize={12}
                    />
                    <YAxis stroke="#52525b" fontSize={12} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a' }}
                        itemStyle={{ color: '#e4e4e7' }}
                        labelFormatter={(label) => new Date(label).toLocaleTimeString()}
                    />
                    <Area type="monotone" dataKey="cost" stroke="#8884d8" fillOpacity={1} fill="url(#colorCost)" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
