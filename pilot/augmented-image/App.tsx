/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useState, useEffect } from 'react';
import { generateInfographic, analyzeImageRegions } from './services/geminiService';
import { AugmentedCanvas } from './components/AugmentedCanvas';
import { LoadingState } from './components/LoadingState';
import { Search, RefreshCw, Volume2, Paperclip, FileText, X } from 'lucide-react';
import { AnalysisResult, GeneratedImage, TechnicalDocument } from './types';
import { motion, AnimatePresence } from 'framer-motion';
import { DashboardSheet } from './components/dashboard/DashboardSheet';

type AppStatus = 'idle' | 'generating' | 'analyzing' | 'complete';

const SUGGESTIONS = [
  "Mercedes AMG A45 S Front Suspension",
  "Explain the MBUX Hyperscreen",
  "Mercedes-Benz Concept CLA Class"
];

const ANALYSIS_PHRASES = [
  "Accessing vehicle diagnostics...",
  "Querying Mercedes-Benz knowledge base...",
  "Analyzing component schematics...",
  "Retrieving technical specifications...",
  "Generating visual overlay..."
];

function App() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<AppStatus>('idle');
  const [isDashboardOpen, setDashboardOpen] = useState(false);
  const [data, setData] = useState<{ image: GeneratedImage; analysis: AnalysisResult | null } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingDocs, setPendingDocs] = useState<TechnicalDocument[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // Analysis phrase state
  const [analysisPhrase, setAnalysisPhrase] = useState(ANALYSIS_PHRASES[0]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    const newDocs: TechnicalDocument[] = [];

    for (const file of Array.from(files)) {
      const f = file as File;
      try {
        const base64 = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve((reader.result as string).split(',')[1]);
          reader.onerror = reject;
          reader.readAsDataURL(f);
        });

        newDocs.push({
          name: f.name,
          mimeType: f.type,
          data: base64
        });
      } catch (err) {
        console.error("Error reading file:", f.name, err);
      }
    }

    setPendingDocs(prev => [...prev, ...newDocs]);
    setIsUploading(false);
  };

  const removeDoc = (index: number) => {
    setPendingDocs(prev => prev.filter((_, i) => i !== index));
  };



  const processSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    // Reset and Start
    setStatus('generating');
    setError(null);
    setData(null);

    try {
      // Step 1: Generate Image
      console.log('Generating image for:', searchQuery);
      const image = await generateInfographic(searchQuery);

      // Update state to show image immediately with scanning overlay
      setData({ image, analysis: null });
      setStatus('analyzing');
      setAnalysisPhrase("Connecting to Intelligence Center..."); // Initial

      // Step 2: Analyze Image with Streaming Logs
      console.log('Analyzing image with documents:', pendingDocs.length);
      const analysis = await analyzeImageRegions(
        searchQuery,
        image.base64,
        pendingDocs,
        (logMessage) => setAnalysisPhrase(logMessage) // Callback updates UI
      );

      console.log('Analysis complete:', analysis);
      setData({ image, analysis });
      setStatus('complete');
      setPendingDocs([]); // Clear after success

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Something went wrong. Please check your network and try again.');
      setStatus('idle');
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    processSearch(query);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    processSearch(suggestion);
  };

  const handleReset = () => {
    setData(null);
    setStatus('idle');
    setQuery('');
    setError(null);
  };

  return (
    <div className="h-screen w-screen bg-[#050505] text-white selection:bg-cyan-500/30 selection:text-cyan-200 overflow-hidden flex flex-col">

      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-900/20 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 w-full h-full flex flex-col p-4 md:p-6">

        {/* Header */}
        <header className="flex-none flex justify-between items-center pb-4">
          <div className="flex items-center gap-2">
            {/* Logo removed */}
          </div>
          <div className="flex gap-4 items-center">
            {status !== 'idle' && (
              <button
                onClick={handleReset}
                className="text-sm text-gray-400 hover:text-white flex items-center gap-2 transition-colors"
              >
                <RefreshCw size={14} /> New Search
              </button>
            )}
            <button
              onClick={() => setDashboardOpen(true)}
              className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-2 transition-colors border border-cyan-500/20 px-3 py-1.5 rounded-full hover:bg-cyan-500/10"
            >
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              Live Dashboard
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 flex flex-col items-center justify-center w-full relative overflow-hidden">

          <AnimatePresence mode="wait">

            {/* IDLE STATE: Search Bar */}
            {status === 'idle' && (
              <motion.div
                key="search"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -20 }}
                className="w-full max-w-xl z-20 px-4 md:px-0"
              >
                <div className="text-center mb-10">
                  <h2 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
                    Ask <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">Alora</span>
                  </h2>
                  <p className="text-gray-400 text-lg">Your Intelligent Mercedes-Benz Co-Pilot</p>
                </div>

                <form onSubmit={handleSearch} className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full opacity-50 group-hover:opacity-100 transition duration-500 blur"></div>
                  <div className="relative bg-black rounded-full flex items-center p-2 pr-4">
                    <Search className="ml-4 text-gray-400 w-6 h-6 shrink-0" />
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Show me the latest AMG engine..."
                      className="w-full bg-transparent text-white p-4 text-lg focus:outline-none placeholder-gray-600"
                    />

                    <label className="p-3 text-gray-400 hover:text-cyan-400 cursor-pointer transition-colors relative group/tooltip">
                      <Paperclip size={20} className={isUploading ? "animate-spin" : ""} />
                      <input type="file" className="hidden" multiple accept=".pdf,.csv,.txt" onChange={handleFileUpload} />
                      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-[10px] rounded opacity-0 group-hover/tooltip:opacity-100 whitespace-nowrap pointer-events-none">
                        Add Technical Context (PDF/CSV)
                      </span>
                    </label>
                    <button
                      type="submit"
                      disabled={!query.trim() || isUploading}
                      className="hidden md:block px-6 py-3 bg-white text-black font-bold rounded-full hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ml-2"
                    >
                      Generate
                    </button>
                  </div>
                </form>

                {/* Pending Docs UI */}
                {pendingDocs.length > 0 && (
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {pendingDocs.map((doc, i) => (
                      <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-xs text-cyan-200">
                        <FileText size={12} />
                        <span className="max-w-[100px] truncate">{doc.name}</span>
                        <button onClick={() => removeDoc(i)} className="hover:text-white transition-colors">
                          <X size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Suggestions Pills */}
                <div className="mt-8 flex flex-wrap justify-center gap-3">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-400 hover:bg-white/10 hover:text-cyan-200 hover:border-cyan-500/30 transition-all duration-300 backdrop-blur-sm"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 bg-red-900/20 border border-red-500/30 rounded-xl text-red-200 text-center text-sm"
                  >
                    {error}
                  </motion.div>
                )}
              </motion.div>
            )}

            {/* GENERATING STATE: Gray Screen Loader */}
            {status === 'generating' && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="w-full h-full flex items-center justify-center"
              >
                <LoadingState />
              </motion.div>
            )}

            {/* ANALYZING & COMPLETE STATES: Image Canvas */}
            {(status === 'analyzing' || status === 'complete') && data && (
              <motion.div
                key="result"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full h-full flex flex-col"
              >
                {status === 'complete' && (
                  <div className="text-center mb-2 flex-none z-20 flex flex-col items-center gap-2">
                    <h2 className="text-xl font-bold text-white capitalize shadow-black drop-shadow-md">{query}</h2>
                    {data.analysis?.audio_url && (
                      <div className="flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full backdrop-blur-md border border-white/10 animate-fade-in-up">
                        <Volume2 size={14} className="text-cyan-400 animate-pulse" />
                        <span className="text-xs text-cyan-200">Playing Audio Commentary...</span>
                        <audio src={data.analysis.audio_url} autoPlay />
                      </div>
                    )}
                  </div>
                )}

                <div className="flex-1 min-h-0 w-full">
                  <AugmentedCanvas
                    image={data.image}
                    analysis={data.analysis}
                    isScanning={status === 'analyzing'}
                  />
                </div>

                {/* Analysis Loading Text */}
                {status === 'analyzing' && (
                  <div className="h-8 flex-none relative flex justify-center items-center w-full overflow-hidden perspective-500 mt-4">
                    <AnimatePresence mode="wait">
                      <motion.p
                        key={analysisPhrase}
                        initial={{ y: 15, opacity: 0, rotateX: 90 }}
                        animate={{ y: 0, opacity: 1, rotateX: 0 }}
                        exit={{ y: -15, opacity: 0, rotateX: -90 }}
                        transition={{ duration: 0.5, ease: "backOut" }}
                        className="text-gray-500 font-mono text-xs md:text-sm tracking-[0.2em] uppercase absolute text-center"
                      >
                        {analysisPhrase}
                      </motion.p>
                    </AnimatePresence>
                  </div>
                )}

              </motion.div>
            )}

          </AnimatePresence>
        </main>

        <DashboardSheet isOpen={isDashboardOpen} onClose={() => setDashboardOpen(false)} />

      </div>
    </div >
  );
}

export default App;