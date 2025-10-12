"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Orb, AgentState } from "@/components/ui/orb";
import { VoiceButton } from "@/components/ui/voice-button";
import { LiveWaveform } from "@/components/ui/live-waveform";
import {
  startAudioRecording,
  stopAudioRecording,
} from "@/lib/audio";

const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
};

export default function Home() {
  const [agentState, setAgentState] = useState<AgentState>(null);
  const [voiceState, setVoiceState] = useState<"idle" | "recording">(
    "idle"
  );
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const outputVolumeRef = useRef(0);

  const userId = "user_" + Math.random().toString(36).substring(7);

  const wsRef = useRef<WebSocket | null>(null); // Use ref for WebSocket instance

  const connectWebSocket = useCallback((isAudioMode: boolean) => {
    if (wsRef.current) {
      wsRef.current.close(); // Close existing connection
    }

    const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const wsUrl = `${wsProtocol}${window.location.hostname}:8000/ws/${userId}?is_audio=${isAudioMode}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`WebSocket connection opened (audio mode: ${isAudioMode}).`);
      setSocket(ws); // Update state for UI to react
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.mime_type === "audio/pcm") {
        setAgentState("talking");
        const audioBlob = new Blob([
          new Uint8Array(
            atob(message.data)
              .split("")
              .map((char) => char.charCodeAt(0))
          ),
        ]);
        const audioUrl = URL.createObjectURL(audioBlob);
        if (audioPlayerRef.current) {
          audioPlayerRef.current.src = audioUrl;
          audioPlayerRef.current.play();
        }
      } else if (message.turn_complete) {
        setAgentState(null);
      }
    };

    ws.onclose = (event) => {
      console.log("WebSocket connection closed.", event.code, event.reason);
      setSocket(null); // Update state
      // No automatic reconnection here; reconnection will be explicit on mode change
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsRef.current = ws; // Store WebSocket instance in ref
  }, [userId]); // userId is a dependency for useCallback

  useEffect(() => {
    connectWebSocket(false); // Connect in text mode initially

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectWebSocket]); // connectWebSocket is a dependency

  const audioRecorderHandler = (pcmData: ArrayBuffer) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const base64String = arrayBufferToBase64(pcmData);
      socket.send(
        JSON.stringify({
          mime_type: "audio/pcm",
          data: base64String,
        })
      );
    }
  };

  const handlePress = async () => {
    if (voiceState === "idle") {
      // Close current text WebSocket and open a new one for audio
      connectWebSocket(true);
      setVoiceState("recording");
      setAgentState("listening");
      await startAudioRecording(audioRecorderHandler);
    } else {
      // Stop recording and switch back to text WebSocket
      stopAudioRecording();
      setVoiceState("idle");
      setAgentState("thinking");
      connectWebSocket(false);
    }
  };

  useEffect(() => {
    let audioContext: AudioContext | null = null;
    let sourceNode: MediaElementAudioSourceNode | null = null;
    let analyserNode: AnalyserNode | null = null;
    let animationFrameId: number | null = null;

    if (audioPlayerRef.current) {
      audioContext = new AudioContext();
      sourceNode = audioContext.createMediaElementSource(
        audioPlayerRef.current
      );
      analyserNode = audioContext.createAnalyser();
      sourceNode.connect(analyserNode);
      analyserNode.connect(audioContext.destination);
      analyserNode.fftSize = 32;
      const bufferLength = analyserNode.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateVolume = () => {
        if (analyserNode) {
          analyserNode.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
          outputVolumeRef.current = average / 255;
        }
        animationFrameId = requestAnimationFrame(updateVolume);
      };
      updateVolume();
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      if (sourceNode) {
        sourceNode.disconnect();
      }
      if (analyserNode) {
        analyserNode.disconnect();
      }
      if (audioContext) {
        audioContext.close();
      }
    };
  }, [audioPlayerRef.current]);

  return (
    <div className="relative flex h-screen w-full flex-col items-center justify-center bg-white dark:bg-black">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px]">
        <Orb agentState={agentState} outputVolumeRef={outputVolumeRef} />
      </div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
        <VoiceButton
          state={voiceState === "recording" ? "recording" : "idle"}
          onPress={handlePress}
          size="icon"
          className="w-24 h-24 rounded-full bg-transparent hover:bg-transparent"
        />
      </div>
      <div className="absolute bottom-20 w-full max-w-md">
        <LiveWaveform
          active={voiceState === "recording"}
          height={40}
          barWidth={3}
          barGap={2}
        />
      </div>
      <audio ref={audioPlayerRef} hidden onEnded={() => setAgentState(null)} />
    </div>
  );
}