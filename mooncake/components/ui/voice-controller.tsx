'use client';

import { useAuth } from '@/context/AuthContext';
import { useAudio } from '@/lib/use-audio';
import { useEffect, useState } from 'react';
import { VoiceButton } from './voice-button';

export const VoiceController = () => {
  const { user } = useAuth();
  const [idToken, setIdToken] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      user.getIdToken().then(setIdToken);
    }
  }, [user]);

  const { audioState, text, startRecording, stopRecording } = useAudio(idToken);

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
        disabled={!user}
      />
      <p>State: {audioState}</p>
      <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px', minHeight: '100px' }}>
        <h2>Agent Response:</h2>
        <p>{text}</p>
      </div>
    </div>
  );
};
