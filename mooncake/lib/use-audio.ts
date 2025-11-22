import { useState, useRef, useCallback } from 'react';

// Helper function to convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

// Helper function to convert Base64 to ArrayBuffer
function base64ToArray(base64: string): ArrayBuffer {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

// Helper function to convert Float32Array to 16-bit PCM
function convertFloat32ToPCM(inputData: Float32Array): ArrayBuffer {
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    pcm16[i] = inputData[i] * 0x7fff;
  }
  return pcm16.buffer;
}

export type AudioState = 'idle' | 'recording' | 'processing' | 'playing';

export const useAudio = (idToken: string | null) => {
  const [audioState, setAudioState] = useState<AudioState>('idle');
  const [text, setText] = useState<string>('');
  const websocketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioRecorderNodeRef = useRef<AudioWorkletNode | null>(null);
  const audioPlayerNodeRef = useRef<AudioWorkletNode | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const audioBufferRef = useRef<Uint8Array[]>([]);
  const bufferTimerRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = useCallback(async () => {
    setAudioState('recording');
    setText('');
    try {
      const audioRecorderContext = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = audioRecorderContext;

      await audioRecorderContext.audioWorklet.addModule('/pcm-recorder-processor.js');

      const micStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } });
      micStreamRef.current = micStream;

      const source = audioRecorderContext.createMediaStreamSource(micStream);
      const audioRecorderNode = new AudioWorkletNode(audioRecorderContext, 'pcm-recorder-processor');
      source.connect(audioRecorderNode);
      audioRecorderNodeRef.current = audioRecorderNode;

      audioRecorderNode.port.onmessage = (event) => {
        const pcmData = convertFloat32ToPCM(event.data);
        audioBufferRef.current.push(new Uint8Array(pcmData));
      };

      if (!bufferTimerRef.current) {
        bufferTimerRef.current = setInterval(sendBufferedAudio, 200);
      }

      // Setup WebSocket
      if (!idToken) {
        console.error("No ID token provided for authentication.");
        setAudioState('idle');
        return;
      }
      
      let wsUrl: string;
      const sessionId = Math.random().toString().substring(10);
      const isLocal = window.location.hostname === 'localhost';

      if (isLocal) {
        // Use non-secure WebSocket for local development
        wsUrl = `ws://localhost:8000/ws/${sessionId}?is_audio=true&token=${idToken}`;
      } else {
        // Use existing logic for deployed environments
        const backendHostname = process.env.NEXT_PUBLIC_PILOT_HOSTNAME || window.location.hostname.replace('3000-', '8000-');
        wsUrl = `wss://${backendHostname}/ws/${sessionId}?is_audio=true&token=${idToken}`;
      }
      
      websocketRef.current = new WebSocket(wsUrl);

      websocketRef.current.onopen = () => console.log("WebSocket connection opened.");
      websocketRef.current.onclose = () => console.log("WebSocket connection closed.");
      websocketRef.current.onerror = (e) => console.error("WebSocket error: ", e);

      websocketRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.interrupted) {
          audioPlayerNodeRef.current?.port.postMessage({ command: "endOfAudio" });
          return;
        }

        if (message.mime_type === 'text/plain') {
          setText(prev => prev + message.data);
        }

        if (message.mime_type === 'audio/pcm') {
          if (!audioPlayerNodeRef.current) {
            startPlayback();
          }
          const audioData = base64ToArray(message.data);
          audioPlayerNodeRef.current?.port.postMessage(audioData, [audioData]);
        }

        if (message.turn_complete) {
          console.log("Backend turn complete.");
          // The user will manually stop the recording, so we don't close the connection here.
        }
      };

    } catch (error) {
      console.error('Error starting recording:', error);
      setAudioState('idle');
    }
  }, [idToken]);

  const sendBufferedAudio = () => {
    if (audioBufferRef.current.length === 0 || !websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    let totalLength = 0;
    for (const chunk of audioBufferRef.current) {
      totalLength += chunk.length;
    }

    const combinedBuffer = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of audioBufferRef.current) {
      combinedBuffer.set(chunk, offset);
      offset += chunk.length;
    }

    websocketRef.current.send(JSON.stringify({
      mime_type: 'audio/pcm',
      data: arrayBufferToBase64(combinedBuffer.buffer),
    }));

    audioBufferRef.current = [];
  };

  const startPlayback = async () => {
    try {
        const playerContext = new AudioContext({ sampleRate: 16000 });
        await playerContext.audioWorklet.addModule('/pcm-player-processor.js');
        const playerNode = new AudioWorkletNode(playerContext, 'pcm-player-processor');
        playerNode.connect(playerContext.destination);
        audioPlayerNodeRef.current = playerNode;
    } catch (error) {
        console.error("Error starting playback:", error);
    }
  };

  const stopRecording = useCallback(() => {
    if (bufferTimerRef.current) {
      clearInterval(bufferTimerRef.current);
      bufferTimerRef.current = null;
    }

    sendBufferedAudio();

    micStreamRef.current?.getTracks().forEach(track => track.stop());
    audioContextRef.current?.close();
    websocketRef.current?.close();

    setAudioState('idle');
  }, []);

  return { audioState, text, startRecording, stopRecording };
};
