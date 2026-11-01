import React from 'react';
import { Search, Sparkles, FileText, CheckCircle2 } from 'lucide-react';

export const Hero3D: React.FC = () => {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 via-slate-900/50 to-slate-950 border border-slate-800 p-6 sm:p-8 mb-6 shadow-2xl">
      {/* Background glow effects */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full filter blur-3xl pointer-events-none -z-0"></div>
      <div className="absolute bottom-0 right-10 w-80 h-80 bg-violet-500/10 rounded-full filter blur-3xl pointer-events-none -z-0"></div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
        {/* Left Copy */}
        <div className="lg:col-span-7 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-cyan-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Verifiable RAG & Lexical Precision</span>
          </div>

          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Enterprise Policy Intelligence <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400">
              Grounded in Verified Citations
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-400 max-w-xl leading-relaxed">
            Ingest governance standards, ISO requirements, and security policies. Ask complex questions and receive deterministic answers backed by verifiable source snippets.
          </p>

          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              <span>Zero Hallucinated Citations</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-violet-400" />
              <span>Semantic Chunk Boundary Preservation</span>
            </div>
          </div>
        </div>

        {/* Right: 3D Floating Document & Evidence Visual */}
        <div className="lg:col-span-5 flex justify-center items-center py-4">
          <div className="relative w-64 h-56 perspective-1000 flex items-center justify-center">
            {/* Ambient Backlight Glow */}
            <div className="absolute inset-4 bg-gradient-to-tr from-cyan-500/20 to-violet-600/20 rounded-2xl animate-glow"></div>

            {/* Document Layer 3 (Bottom) */}
            <div
              className="absolute w-48 h-36 rounded-xl bg-slate-900 border border-slate-700/60 shadow-2xl p-3 opacity-60 animate-float-2 transform origin-center"
              style={{ transform: 'rotateX(25deg) rotateY(-18deg) rotateZ(6deg) translateZ(-40px)' }}
            >
              <div className="w-16 h-2 bg-slate-700/70 rounded mb-2"></div>
              <div className="space-y-1.5">
                <div className="w-full h-1 bg-slate-800 rounded"></div>
                <div className="w-5/6 h-1 bg-slate-800 rounded"></div>
              </div>
            </div>

            {/* Document Layer 2 (Middle) */}
            <div
              className="absolute w-52 h-40 rounded-xl bg-slate-900/95 border border-slate-700/80 shadow-2xl p-4 opacity-85 transform origin-center"
              style={{ transform: 'rotateX(22deg) rotateY(-16deg) rotateZ(4deg) translateZ(-15px) translateY(-8px)' }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="w-20 h-2.5 bg-violet-400/50 rounded"></div>
                <FileText className="w-3.5 h-3.5 text-violet-400" />
              </div>
              <div className="space-y-1.5">
                <div className="w-full h-1.5 bg-slate-800 rounded"></div>
                <div className="w-4/5 h-1.5 bg-slate-800 rounded"></div>
                <div className="w-3/4 h-1.5 bg-slate-800 rounded"></div>
              </div>
            </div>

            {/* Document Layer 1 (Top Active Document) */}
            <div
              className="absolute w-56 h-44 rounded-xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-cyan-500/50 shadow-2xl shadow-cyan-500/10 p-4.5 animate-float-1 transform origin-center z-20"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                  <span className="text-[10px] font-mono font-bold text-cyan-300">SECURITY_POLICY.PDF</span>
                </div>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-mono">
                  PAGE 1
                </span>
              </div>

              <div className="space-y-2">
                <div className="w-full h-1.5 bg-slate-800 rounded"></div>
                <div className="w-full h-1.5 bg-cyan-400/30 rounded"></div>
                <div className="w-4/6 h-1.5 bg-slate-800 rounded"></div>
              </div>

              {/* Verified Evidence Highlight Tag */}
              <div className="mt-4 p-2 rounded-lg bg-cyan-950/70 border border-cyan-500/40 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Search className="w-3 h-3 text-cyan-400" />
                  <span className="text-[10px] text-cyan-200 font-mono">Evidence Verified</span>
                </div>
                <span className="text-[9px] font-mono text-cyan-400 font-bold">98.5%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
