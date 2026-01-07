
import React from 'react';
import { StreamEvent } from './useDatadogStream';
import { Terminal } from 'lucide-react';

export function WidgetStream({ events }: { events: StreamEvent[] }) {
    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 h-64 flex flex-col">
            <h3 className="text-zinc-400 text-sm font-medium mb-4 flex items-center gap-2">
                <Terminal className="w-4 h-4" /> Live LLM Trace Stream
            </h3>
            <div className="flex-1 overflow-y-auto space-y-2 pr-2 font-mono text-[10px]">
                {events.map((event) => (
                    <div key={event.id} className="flex gap-2 items-start opacity-80 hover:opacity-100">
                        <span className="text-zinc-500 shrink-0">{event.time}</span>
                        <span className={`shrink-0 ${event.level === 'error' ? 'text-red-400' : 'text-blue-400'
                            }`}>
                            [{event.source.toUpperCase()}]
                        </span>
                        <span className="text-zinc-300 break-all">{event.message}</span>
                    </div>
                ))}
                {events.length === 0 && (
                    <div className="text-zinc-600 italic">Waiting for events...</div>
                )}
            </div>
        </div>
    );
}
