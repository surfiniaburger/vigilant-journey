import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VoiceController } from '@/components/ui/voice-controller';
import { useAudio } from '@/lib/use-audio';
import { useAuth } from '@/context/AuthContext';

// Mock the useAudio hook
jest.mock('@/lib/use-audio');
// Mock the useAuth hook
jest.mock('@/context/AuthContext');

// Type assertion for the mocked hooks
const useAudioMock = useAudio as jest.Mock;
const useAuthMock = useAuth as jest.Mock;

describe('VoiceController', () => {
  const startRecordingMock = jest.fn();
  const stopRecordingMock = jest.fn();

  beforeEach(() => {
    // Reset mocks before each test
    startRecordingMock.mockClear();
    stopRecordingMock.mockClear();
    useAuthMock.mockClear();

    // Provide a mock user for the useAuth hook
    useAuthMock.mockReturnValue({
      user: {
        getIdToken: async () => 'test-token',
      },
    });
  });

  it('renders in idle state and calls startRecording on press', async () => {
    // Provide the mock return value for this specific test
    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });

    render(<VoiceController />);

    await waitFor(() => {
      expect(screen.getByText('State: idle')).toBeInTheDocument();
    });

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();

    // Simulate a user press
    fireEvent.click(button);

    // Assert that startRecording was called
    expect(startRecordingMock).toHaveBeenCalledTimes(1);
    expect(stopRecordingMock).not.toHaveBeenCalled();
  });

  it('renders in recording state and calls stopRecording on press', async () => {
    // Provide the mock return value for this specific test
    useAudioMock.mockReturnValue({
      audioState: 'recording',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });

    render(<VoiceController />);

    await waitFor(() => {
      expect(screen.getByText('State: recording')).toBeInTheDocument();
    });

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();

    // Simulate a user press
    fireEvent.click(button);

    // Assert that stopRecording was called
    expect(stopRecordingMock).toHaveBeenCalledTimes(1);
    expect(startRecordingMock).not.toHaveBeenCalled();
  });

  it('displays the text from the backend', async () => {
    const sampleText = 'Hello, this is a test.';
    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: sampleText,
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });

    render(<VoiceController />);

    await waitFor(() => {
      expect(screen.getByText(sampleText)).toBeInTheDocument();
    });
  });

  it('disables the button when there is no user', async () => {
    // Mock useAuth to return no user for this test
    useAuthMock.mockReturnValue({ user: null });

    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    });

    render(<VoiceController />);

    await waitFor(() => {
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
    });
  });
});