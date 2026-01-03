/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useState, useRef, useEffect } from 'react';
import { Segment } from '../../types';
import { motion } from 'framer-motion';
import { Loader2, Play, Pause } from 'lucide-react';

interface WidgetProps {
  segment: Segment;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080';

// ----------------------------------------------------------------------
// Audio Component (ElevenLabs Inspired)
// ----------------------------------------------------------------------

// Canvas-based Waveform Visualizer
interface WaveformProps {
  isPlaying: boolean;
  color?: string;
}

const WaveformCanvas = ({ isPlaying, color = "rgba(6, 182, 212, 1)" }: WaveformProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let timeOffset = 0;

    const animate = () => {
      // Reset canvas
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      // Layout config
      const barWidth = 3;
      const gap = 2;
      const barCount = Math.floor(width / (barWidth + gap));
      const centerY = height / 2;

      ctx.fillStyle = color;
      timeOffset += 0.1;

      for (let i = 0; i < barCount; i++) {
        // Static seed + Sine wave modulation
        const staticHeight = Math.sin(i * 0.5) * 0.3 + 0.4;

        // Dynamic movement when playing
        const dynamicMod = isPlaying ? Math.sin(timeOffset + i * 0.5) * 0.3 : 0;

        const finalBarHeightRatio = Math.max(0.1, Math.min(1.0, staticHeight + dynamicMod));
        const finalBarHeight = finalBarHeightRatio * height;

        const x = i * (barWidth + gap);
        const y = centerY - (finalBarHeight / 2);

        // Rounded Rect manually
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, finalBarHeight, 2);
        ctx.fill();
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationRef.current);
  }, [isPlaying, color]);

  return <canvas ref={canvasRef} width={120} height={32} className="w-[120px] h-[32px]" />;
};

const AudioPlayer = ({ text }: { text: string }) => {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handlePlay = async () => {
    console.log("▶️ Play Clicked");
    if (isPlaying) {
      console.log("⏸️ Pausing");
      audioRef.current?.pause();
      setIsPlaying(false);
      return;
    }

    if (audioUrl) {
      console.log("🔊 Resuming existing audio");
      audioRef.current?.play();
      setIsPlaying(true);
      return;
    }

    setIsLoading(true);
    console.log("⏳ Fetching audio...");
    try {
      const response = await fetch(`${BACKEND_URL}/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) throw new Error("TTS Failed");
      const data = await response.json();
      console.log("✅ Audio URL received:", data.audio_url);
      setAudioUrl(data.audio_url);

      setTimeout(() => {
        if (audioRef.current) {
          audioRef.current.src = data.audio_url;
          audioRef.current.play().then(() => {
            console.log("🔊 Playing started");
            setIsPlaying(true);
          }).catch(e => console.error("❌ Audio Play Error:", e));
        }
      }, 100);

    } catch (e) {
      console.error("❌ Synthesis Error:", e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-8 flex items-center gap-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-full pl-2 pr-6 py-2 shadow-2xl animate-fade-in-up hover:border-cyan-500/30 transition-colors w-fit mx-auto md:mx-0 cursor-pointer pointer-events-auto z-50">
      <button
        onClick={(e) => {
          e.stopPropagation(); // Prevent widget click issues
          handlePlay();
        }}
        disabled={isLoading}
        className="flex items-center justify-center w-10 h-10 bg-white hover:bg-cyan-50 text-black rounded-full transition-transform active:scale-95 disabled:opacity-50 shadow-lg shadow-white/5"
      >
        {isLoading ? (
          <Loader2 size={18} className="animate-spin text-black" />
        ) : isPlaying ? (
          <Pause size={18} className="fill-current ml-0.5" />
        ) : (
          <Play size={18} className="fill-current ml-1" />
        )}
      </button>

      {/* Waveform Visualizer */}
      <div className="flex flex-col gap-0.5 select-none" onClick={(e) => {
        e.stopPropagation();
        handlePlay();
      }}>
        <span className="text-[9px] font-bold text-gray-500 uppercase tracking-[0.2em]">Audio Insight</span>
        <WaveformCanvas isPlaying={isPlaying} color={isPlaying ? "rgba(34, 211, 238, 1)" : "rgba(100, 116, 139, 0.5)"} />
      </div>

      <audio
        ref={audioRef}
        onEnded={() => {
          console.log("⏹️ Audio Ended");
          setIsPlaying(false);
        }}
        onError={(e) => console.error("❌ Audio Tag Error", e)}
        className="hidden"
      />
    </div>
  );
}

// ----------------------------------------------------------------------
// Shared Styles
// ----------------------------------------------------------------------
// Max height set to 80vh to ensure it fits on screen when centered
const GLASS_PANEL = "bg-black/90 backdrop-blur-xl border border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.6)] w-full max-h-[80vh] overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent";

// ----------------------------------------------------------------------
// Sub-components for different formats
// ----------------------------------------------------------------------

const MiniWidget: React.FC<WidgetProps> = ({ segment }) => (
  <motion.div
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    className="bg-black/95 backdrop-blur-md border border-cyan-500/30 px-6 py-3 rounded-full flex items-center gap-4 shadow-[0_0_30px_rgba(0,0,0,0.5)] mx-auto w-fit"
  >
    <span className="text-2xl shrink-0">{segment.icon || '✨'}</span>
    <span className="text-lg font-bold text-white tracking-wide">{segment.label}</span>
  </motion.div>
);

const CompactWidget: React.FC<WidgetProps> = ({ segment }) => (
  <motion.div
    className={`${GLASS_PANEL} p-6 rounded-2xl relative group`}
  >
    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-cyan-500 via-purple-500 to-transparent opacity-70" />

    <div className="flex items-start gap-5 mb-4">
      <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-3xl shadow-inner shrink-0">
        {segment.icon || '🔍'}
      </div>
      <div className="min-w-0 flex-1 pt-1">
        <div className="text-xs uppercase tracking-[0.2em] text-cyan-400 font-bold mb-1 truncate">{segment.category || 'Concept'}</div>
        <h3 className="font-bold text-white text-2xl leading-tight break-words">{segment.label}</h3>
      </div>
    </div>

    <p className="text-base text-gray-300 leading-relaxed font-light">
      {segment.description}
    </p>
  </motion.div>
);

const StatsWidget: React.FC<WidgetProps> = ({ segment }) => (
  <motion.div
    className={`${GLASS_PANEL} p-6 rounded-2xl relative`}
  >
    <div className="flex justify-between items-center mb-5 pb-5 border-b border-white/5 sticky top-0 bg-black/90 backdrop-blur-xl z-10 -mx-6 px-6 -mt-6 pt-6 rounded-t-2xl">
      <h3 className="font-bold text-white text-xl flex items-center gap-3 truncate pr-2">
        <span className="text-2xl">{segment.icon || '📊'}</span>
        <span className="truncate">{segment.label}</span>
      </h3>
      <div className="px-3 py-1 rounded text-[10px] font-bold bg-purple-500/20 text-purple-200 uppercase tracking-wider border border-purple-500/20 shrink-0">Data</div>
    </div>

    <div className="grid grid-cols-2 gap-4">
      {segment.stats?.map((stat, idx) => (
        <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-cyan-500/30 transition-colors">
          <div className="text-cyan-400 font-mono font-bold text-xl truncate">{stat.value}</div>
          <div className="text-xs text-gray-500 uppercase tracking-wide mt-1 truncate">{stat.label}</div>
        </div>
      ))}
      {(!segment.stats || segment.stats.length === 0) && (
        <div className="col-span-2 text-sm text-gray-500 italic p-4 text-center">
          Detailed metrics unavailable.
        </div>
      )}
    </div>
    <p className="mt-5 text-sm text-gray-400 border-t border-white/5 pt-4 leading-relaxed">{segment.description}</p>
  </motion.div>
);

const DetailedWidget: React.FC<WidgetProps> = ({ segment }) => (
  <motion.div
    className={`${GLASS_PANEL} p-0 rounded-2xl flex flex-col`}
  >
    {/* Header */}
    <div className="bg-gradient-to-br from-zinc-900 to-black border-b border-white/10 p-6 relative overflow-hidden shrink-0">
      <div className="absolute top-[-30px] right-[-30px] w-32 h-32 bg-cyan-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-[-30px] left-[-30px] w-32 h-32 bg-purple-500/20 rounded-full blur-3xl" />

      <div className="relative z-10">
        <div className="flex justify-between items-start mb-3">
          <span className="inline-block px-3 py-1 rounded text-[10px] font-bold bg-white/10 text-cyan-200 border border-cyan-500/20 uppercase tracking-wide">
            {segment.category || 'Deep Dive'}
          </span>
          <span className="text-4xl filter drop-shadow-glow shrink-0 ml-3">{segment.icon || '🚀'}</span>
        </div>
        <h3 className="font-bold text-3xl text-white mb-2 leading-tight break-words">{segment.label}</h3>
        <div className="w-16 h-1.5 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full" />
      </div>
    </div>

    {/* Content */}
    <div className="p-6 bg-black/40">
      <p className="text-base text-gray-300 leading-relaxed mb-6 font-light">
        {segment.description}
      </p>

      {segment.stats && segment.stats.length > 0 && (
        <div className="flex gap-4 mb-6 overflow-x-auto pb-2 scrollbar-none">
          {segment.stats.map((stat, i) => (
            <div key={i} className="flex-shrink-0 bg-white/5 rounded-lg px-4 py-3 border border-white/5 min-w-[100px]">
              <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wider truncate">{stat.label}</div>
              <div className="text-white font-mono font-medium text-lg truncate">{stat.value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  </motion.div>
);

// ----------------------------------------------------------------------
// Main Factory
// ----------------------------------------------------------------------

export const WidgetEngine: React.FC<WidgetProps> = ({ segment }) => {
  const content = (() => {
    switch (segment.format) {
      case 'mini': return <MiniWidget segment={segment} />;
      case 'stats': return <StatsWidget segment={segment} />;
      case 'detailed': return <DetailedWidget segment={segment} />;
      case 'compact':
      default: return <CompactWidget segment={segment} />;
    }
  })();

  if (segment.format === 'mini') return content;

  return (
    <div className="flex flex-col relative w-full">
      {content}

      {segment.description && (
        <div className="flex justify-start px-2">
          {/* Auto-injected player below content */}
          <AudioPlayer text={segment.description} />
        </div>
      )}
    </div>
  );
};