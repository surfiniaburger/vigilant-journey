
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { WidgetAgents } from './WidgetAgents';

const mockAgents = [
    { name: 'ResearchAgent', calls: 150, latency: 450, errorRate: 0 },
    { name: 'CritiqueAgent', calls: 45, latency: 1200, errorRate: 0.05 },
];

describe('WidgetAgents', () => {
    it('renders agent performance data correctly', () => {
        render(<WidgetAgents agents={mockAgents} />);

        expect(screen.getByText('Agent Performance')).toBeInTheDocument();
        expect(screen.getByText('ResearchAgent')).toBeInTheDocument();
        expect(screen.getByText('CritiqueAgent')).toBeInTheDocument();
        expect(screen.getByText('150')).toBeInTheDocument();
        expect(screen.getByText('450ms')).toBeInTheDocument();
    });

    it('renders "OK" status for 0 error rate', () => {
        render(<WidgetAgents agents={mockAgents} />);
        const okStatus = screen.getByText('OK');
        expect(okStatus).toBeInTheDocument();
        expect(okStatus).toHaveClass('text-emerald-400');
    });

    it('renders "Err" status for non-zero error rate', () => {
        render(<WidgetAgents agents={mockAgents} />);
        const errStatus = screen.getByText('Err');
        expect(errStatus).toBeInTheDocument();
        expect(errStatus).toHaveClass('text-red-400');
    });
});
