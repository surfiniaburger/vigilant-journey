'use client';

import { useAudio } from '@/lib/use-audio';
import { VoiceButton } from './voice-button';

export const VoiceController = () => {
  const { audioState, text, startRecording, stopRecording } = useAudio();

  const handleToggleRecording = () => {
    if (audioState === 'recording') {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div>
      <VoiceButton
        state={audioState === 'recording' ? 'recording' : 'idle'}
        onPress={handleToggleRecording}
        label="Voice"
        trailing="Click to record"
      />
      <p>State: {audioState}</p>
      <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px', minHeight: '100px' }}>
        <h2>Agent Response:</h2>
        <p>{text}</p>
      </div>
    </div>
  );
};
