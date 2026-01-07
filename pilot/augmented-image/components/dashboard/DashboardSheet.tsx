
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Activity } from 'lucide-react';
import { useDatadogStream } from './useDatadogStream';
import { WidgetCost } from './WidgetCost';
import { WidgetAgents } from './WidgetAgents';
import { WidgetStream } from './WidgetStream';

interface DashboardSheetProps {
    isOpen: boolean;
    onClose: () => void;
}

export function DashboardSheet({ isOpen, onClose }: DashboardSheetProps) {
    const { metrics, agents, stream } = useDatadogStream(isOpen);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
                    />

                    {/* Sheet */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                        className="fixed right-0 top-0 h-full w-full md:w-[480px] bg-zinc-950 border-l border-zinc-800 z-50 shadow-2xl overflow-y-auto"
                    >
                        <div className="p-6 space-y-6">
                            {/* Header */}
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
                                        <Activity className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-semibold text-white">Live Observability</h2>
                                        <p className="text-xs text-zinc-500">Datadog Real-time Stream</p>
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 hover:bg-zinc-800 rounded-full text-zinc-400 hover:text-white transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Top Metrics Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-zinc-900/50 p-3 rounded-lg border border-zinc-800">
                                    <span className="text-xs text-zinc-500 uppercase">Input Token Cost</span>
                                    <div className="text-xl font-mono text-purple-400">96.1¢</div>
                                </div>
                                <div className="bg-zinc-900/50 p-3 rounded-lg border border-zinc-800">
                                    <span className="text-xs text-zinc-500 uppercase">Avg Latency</span>
                                    <div className="text-xl font-mono text-emerald-400">142ms</div>
                                </div>
                            </div>

                            <WidgetCost data={metrics} />

                            <WidgetStream events={stream} />

                            <WidgetAgents agents={agents} />

                            <div className="text-center pt-8 pb-4">
                                <p className="text-[10px] text-zinc-600 uppercase tracking-widest">
                                    Powered by Datadog & CoinPulse Architecture
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
