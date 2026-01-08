
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';
import * as geminiService from './services/geminiService';

// Mock the services
vi.mock('./services/geminiService', () => ({
    generateInfographic: vi.fn(),
    analyzeImageRegions: vi.fn(),
}));

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', async () => {
    const actual = await vi.importActual('framer-motion');
    return {
        ...actual,
        motion: {
            ...actual.motion,
            div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
            p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
        },
        AnimatePresence: ({ children }: any) => <>{children}</>,
    };
});

describe('App Integration Flow', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('completes the full user flow from search to result', async () => {
        const mockImage = { base64: 'mock-base64', mimeType: 'image/png', groundingUrls: [] };
        const mockAnalysis = {
            segments: [
                {
                    label: 'Test Component',
                    format: 'compact',
                    description: 'A test description for the component.',
                    category: 'structure',
                    icon: '🔧',
                    bounds: { x: 10, y: 10, width: 20, height: 20 },
                    audio_intro: 'This is a test component.'
                }
            ],
            audio_url: 'http://example.com/audio.mp3'
        };

        vi.mocked(geminiService.generateInfographic).mockImplementation(async () => {
            await new Promise(r => setTimeout(r, 10));
            return mockImage;
        });
        vi.mocked(geminiService.analyzeImageRegions).mockImplementation(async () => {
            await new Promise(r => setTimeout(r, 10));
            return mockAnalysis;
        });

        render(<App />);

        // 1. Initial State: Check for search bar
        const input = screen.getByPlaceholderText(/Show me the latest AMG engine/i);
        const button = screen.getByRole('button', { name: /Generate/i });

        // 2. User Input
        fireEvent.change(input, { target: { value: 'Mercedes Suspension' } });
        fireEvent.click(button);

        // 3. Generating State
        expect(geminiService.generateInfographic).toHaveBeenCalledWith('Mercedes Suspension');

        // 4. Analyzing State
        await waitFor(() => {
            expect(geminiService.analyzeImageRegions).toHaveBeenCalled();
        }, { timeout: 4000 });

        // 5. Complete State
        await waitFor(() => {
            expect(screen.getByText('Mercedes Suspension')).toBeInTheDocument();
        }, { timeout: 4000 });

        // 6. Interaction: Hover over segment
        const hitbox = screen.getByTestId('segment-hitbox-0');
        fireEvent.mouseEnter(hitbox);

        // Analysis text should now appear in the modal (WidgetEngine)
        await waitFor(() => {
            expect(screen.getByText('Test Component')).toBeInTheDocument();
        });

        expect(screen.getByText(/Playing Audio Commentary/i)).toBeInTheDocument();
    });

    it('handles errors during generation gracefully', async () => {
        (geminiService.generateInfographic as any).mockRejectedValue(new Error('Generation Failed'));

        render(<App />);

        const input = screen.getByPlaceholderText(/Show me the latest AMG engine/i);
        const button = screen.getByRole('button', { name: /Generate/i });

        fireEvent.change(input, { target: { value: 'Error Test' } });
        fireEvent.click(button);

        await waitFor(() => {
            expect(screen.getByText(/Generation Failed/i)).toBeInTheDocument();
        });
    });
});
