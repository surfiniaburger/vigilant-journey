import React from 'react';
import { ErrorBoundary as DatadogErrorBoundary } from '@datadog/browser-rum-react';

function ErrorFallback({ resetError, error }: { resetError: () => void, error: Error }) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-950 text-white p-4">
            <div className="max-w-md w-full bg-neutral-900 rounded-lg p-6 border border-neutral-800 shadow-xl">
                <h2 className="text-xl font-bold text-red-500 mb-4">Application Error</h2>
                <p className="text-neutral-400 mb-4">
                    Something went wrong. The error has been logged.
                </p>
                <pre className="bg-black/50 p-4 rounded text-sm text-red-400 overflow-auto mb-6 max-h-48">
                    {String(error)}
                </pre>
                <button
                    onClick={resetError}
                    className="w-full py-2 px-4 bg-white text-black font-medium rounded hover:bg-neutral-200 transition-colors"
                >
                    Retry
                </button>
            </div>
        </div>
    );
}

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
    return (
        <DatadogErrorBoundary fallback={ErrorFallback}>
            {children}
        </DatadogErrorBoundary>
    );
}
