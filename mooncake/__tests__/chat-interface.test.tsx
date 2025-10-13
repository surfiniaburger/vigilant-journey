'use client';

import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatInterface } from '@/components/ui/chat-interface';
import { useAudio } from '@/lib/use-audio';

// Mock the useAudio hook
jest.mock('@/lib/use-audio');

const useAudioMock = useAudio as jest.Mock;

describe('ChatInterface', () => {
  const startRecordingMock = jest.fn();
  const stopRecordingMock = jest.fn();

  beforeEach(() => {
    startRecordingMock.mockClear();
    stopRecordingMock.mockClear();
    // Set a default mock implementation for all tests
    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });
  });

  it('should render correctly in its initial state', () => {
    render(<ChatInterface />);
    expect(screen.getByRole('button')).toBeInTheDocument();
    // Initially, there are no messages
    expect(screen.queryByRole('log')).not.toBeEmptyDOMElement();
  });

  it('should call startRecording and show user message placeholder on button press in idle state', () => {
    render(<ChatInterface />);
    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(startRecordingMock).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Listening...')).toBeInTheDocument();
  });

  it('should call stopRecording on button press in recording state', () => {
    useAudioMock.mockReturnValue({
      audioState: 'recording',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });

    render(<ChatInterface />);
    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(stopRecordingMock).toHaveBeenCalledTimes(1);
  });

  it('should display and update agent messages as text streams in', () => {
    const { rerender } = render(<ChatInterface />);

    // Simulate first chunk of text from agent
    act(() => {
      useAudioMock.mockReturnValue({
        ...useAudioMock(),
        text: 'Hello',
      });
    });
    rerender(<ChatInterface />);
    expect(screen.getByText('Hello')).toBeInTheDocument();

    // Simulate second chunk of text
    act(() => {
      useAudioMock.mockReturnValue({
        ...useAudioMock(),
        text: 'Hello there',
      });
    });
    rerender(<ChatInterface />);
    expect(screen.getByText('Hello there')).toBeInTheDocument();
    // Ensure it updated the existing message, not created a new one
    const messages = screen.getAllByRole('log'); // Assuming Conversation has role='log'
    expect(messages[0].children).toHaveLength(1);
  });
});
