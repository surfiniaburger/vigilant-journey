import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import { VoiceController } from '@/components/ui/voice-controller'
import { useAudio } from '@/lib/use-audio'

// Mock the useAudio hook
jest.mock('@/lib/use-audio')

// Type assertion for the mocked hook
const useAudioMock = useAudio as jest.Mock

describe('VoiceController', () => {
  const startRecordingMock = jest.fn()
  const stopRecordingMock = jest.fn()

  beforeEach(() => {
    // Reset mocks before each test
    startRecordingMock.mockClear()
    stopRecordingMock.mockClear()
  })

  it('renders in idle state and calls startRecording on press', () => {
    // Provide the mock return value for this specific test
    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    })

    render(<VoiceController />)

    // Check that the component renders correctly in idle state
    expect(screen.getByText('State: idle')).toBeInTheDocument()
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()

    // Simulate a user press
    fireEvent.click(button)

    // Assert that startRecording was called
    expect(startRecordingMock).toHaveBeenCalledTimes(1)
    expect(stopRecordingMock).not.toHaveBeenCalled()
  })

  it('renders in recording state and calls stopRecording on press', () => {
    // Provide the mock return value for this specific test
    useAudioMock.mockReturnValue({
      audioState: 'recording',
      text: '',
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    })

    render(<VoiceController />)

    // Check that the component renders correctly in recording state
    expect(screen.getByText('State: recording')).toBeInTheDocument()
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()

    // Simulate a user press
    fireEvent.click(button)

    // Assert that stopRecording was called
    expect(stopRecordingMock).toHaveBeenCalledTimes(1)
    expect(startRecordingMock).not.toHaveBeenCalled()
  })

  it('displays the text from the backend', () => {
    const sampleText = 'Hello, this is a test.'
    useAudioMock.mockReturnValue({
      audioState: 'idle',
      text: sampleText,
      startRecording: startRecordingMock,
      stopRecording: stopRecordingMock,
    })

    render(<VoiceController />)

    expect(screen.getByText(sampleText)).toBeInTheDocument()
  })
})
