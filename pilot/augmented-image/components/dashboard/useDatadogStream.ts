
import { useState, useEffect } from 'react';

// Types mimicking Datadog Schema
export interface DashboardMetrics {
    timestamp: number;
    cost: number;        // In Nano-Dollars
    tokens: number;
}

export interface AgentStat {
    name: string;
    calls: number;
    latency: number;     // ms
    errorRate: number;   // %
}

export interface StreamEvent {
    id: string;
    time: string;
    message: string;
    level: 'info' | 'warn' | 'error';
    source: 'llm' | 'system' | 'agent';
}

const AGENTS = ['IntelligenceCenter', 'SearchAgent', 'DeepResearch', 'DecisionAgent', 'SafetyCheck'];
const MESSAGES = [
    "Generating embedding for query...",
    "Vertex AI: Token limit check passed",
    "SearchAgent: Finding results for 'Mercedes specs'",
    "Model Armor: PII check passed",
    "Analysis complete. 4 citations found.",
    "Memory Bank: Recall successful (score: 0.89)",
];

export const useDatadogStream = (isActive: boolean) => {
    const [metrics, setMetrics] = useState<DashboardMetrics[]>([]);
    const [agents, setAgents] = useState<AgentStat[]>(AGENTS.map(name => ({ name, calls: 0, latency: 0, errorRate: 0 })));
    const [stream, setStream] = useState<StreamEvent[]>([]);

    // Initial Seed
    useEffect(() => {
        const initialData = Array.from({ length: 20 }).map((_, i) => ({
            timestamp: Date.now() - (20 - i) * 2000,
            cost: Math.random() * 50 + 10,
            tokens: Math.floor(Math.random() * 500 + 100)
        }));
        setMetrics(initialData);
    }, []);

    // Live Stream Simulation
    useEffect(() => {
        if (!isActive) return;

        const interval = setInterval(() => {
            const now = Date.now();

            // 1. Update Metrics (Cost Graph)
            setMetrics(prev => {
                const next = [...prev, {
                    timestamp: now,
                    cost: Math.random() > 0.8 ? Math.random() * 200 : Math.random() * 40, // Random Spikes
                    tokens: Math.floor(Math.random() * 100)
                }];
                return next.slice(-30); // Keep last 30 points
            });

            // 2. Update Agents (Top List)
            setAgents(prev => prev.map(a => ({
                ...a,
                calls: a.calls + (Math.random() > 0.7 ? 1 : 0),
                latency: Math.floor(Math.random() * 200 + 50), // 50-250ms
                errorRate: Math.random() > 0.95 ? 5 : 0 // Occasional error blip
            })).sort((a, b) => b.calls - a.calls)); // Re-sort by busy-ness

            // 3. Update Stream (Logs)
            if (Math.random() > 0.5) {
                const msg = MESSAGES[Math.floor(Math.random() * MESSAGES.length)];
                const isError = Math.random() > 0.95;
                setStream(prev => [{
                    id: Math.random().toString(36).substring(7),
                    time: new Date().toLocaleTimeString(),
                    message: isError ? "Connection Timeout: ElevenLabs API" : msg,
                    level: isError ? 'error' : 'info',
                    source: 'llm'
                }, ...prev].slice(0, 15)); // Keep last 15 logs
            }

        }, 2000); // Update every 2s

        return () => clearInterval(interval);
    }, [isActive]);

    return { metrics, agents, stream };
};
