
import React from 'react';
import { AgentStat } from './useDatadogStream';
import { BarChart2, Activity } from 'lucide-react';

export function WidgetAgents({ agents }: { agents: AgentStat[] }) {
    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
            <h3 className="text-zinc-400 text-sm font-medium mb-4 flex items-center gap-2">
                <BarChart2 className="w-4 h-4" /> Agent Performance
            </h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                    <thead>
                        <tr className="text-zinc-500 border-b border-zinc-800">
                            <th className="pb-2">Agent Name</th>
                            <th className="pb-2 text-right">Calls (1w)</th>
                            <th className="pb-2 text-right">Latency</th>
                            <th className="pb-2 text-right">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {agents.map((agent) => (
                            <tr key={agent.name} className="border-b border-zinc-800/50 hover:bg-zinc-800/20 transition-colors">
                                <td className="py-2 text-zinc-300 font-medium">{agent.name}</td>
                                <td className="py-2 text-right text-zinc-400">{agent.calls}</td>
                                <td className="py-2 text-right text-zinc-400">{agent.latency}ms</td>
                                <td className="py-2 text-right">
                                    {agent.errorRate > 0 ? (
                                        <span className="text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded">Err</span>
                                    ) : (
                                        <span className="text-emerald-400 bg-emerald-400/10 px-1.5 py-0.5 rounded">OK</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
