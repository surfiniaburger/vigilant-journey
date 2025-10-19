'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useAudio } from '@/lib/use-audio';
import { Map } from '@/components/ui/map';
import { VoiceButton } from '@/components/ui/voice-button';
import { Response } from '@/components/ui/response';

interface MapCommand {
  action: 'set_map_center';
  lat: number;
  lng: number;
}

export default function MapPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [idToken, setIdToken] = useState<string | null>(null);

  // Get the token once the user is available
  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
    } else if (user) {
      user.getIdToken().then(setIdToken);
    }
  }, [user, loading, router]);

  // Initialize the audio hook only when we have a token
  const { audioState, text, startRecording, stopRecording } = useAudio(idToken);

  const [mapCenter, setMapCenter] = useState({ lat: 37.7704, lng: -122.3985 });
  const [agentResponse, setAgentResponse] = useState('');

  const handleToggleRecording = () => {
    if (audioState === 'recording') {
      stopRecording();
    } else {
      setAgentResponse('');
      startRecording();
    }
  };

  const isJsonString = (str: string) => {
    if (!str.trim().startsWith('{')) return false;
    try {
      JSON.parse(str);
    } catch (e) {
      return false;
    }
    return true;
  };

  // Effect to process agent responses
  useEffect(() => {
    if (text) {
      if (isJsonString(text)) {
        try {
          const command: MapCommand = JSON.parse(text);
          if (command.action === 'set_map_center') {
            setMapCenter({ lat: command.lat, lng: command.lng });
            setAgentResponse(`Panning map to new location.`);
            return;
          }
        } catch (e) { /* Not a valid command, fall through */ }
      }
      setAgentResponse(text);
    }
  }, [text]);

  // Loading state while checking auth
  if (loading || !user || !idToken) {
    return <div className="w-full h-screen flex items-center justify-center bg-background">Authenticating...</div>;
  }

  // The correct UI
  return (
    <div className="w-full h-screen relative">
      <Map center={mapCenter} />

      {agentResponse && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-sm text-white p-4 rounded-lg max-w-md shadow-lg animate-in fade-in-50">
          <Response>{agentResponse}</Response>
        </div>
      )}

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2">
        <VoiceButton
          state={audioState === 'recording' ? 'recording' : 'idle'}
          onPress={handleToggleRecording}
          size="icon"
          className="w-16 h-16"
        />
      </div>
    </div>
  );
}
