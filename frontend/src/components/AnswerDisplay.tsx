import React, { useState } from 'react';
import type { Answer, Citation } from '../types/api';
import { CheckCircle2, AlertTriangle, Quote, FileText, ChevronRight, X, ShieldCheck } from 'lucide-react';

interface AnswerDisplayProps {
  answer: Answer | null;
  loading: boolean;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer, loading }) => {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  if (loading) {
    return (
      <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-8 shadow-xl text-center py-16 space-y-4">
        <div className="inline-flex p-4 bg-cyan-950/60 border border-cyan-800/40 rounded-2xl text-cyan-400 animate-pulse">
          <Quote className="w-8 h-8" />
        </div>
        <div className="space-y-1">
          <p className="text-sm font-semibold text-slate-200">Executing Semantic & Lexical Retrieval...</p>
          <p className="text-xs text-slate-400 font-mono">Synthesizing grounded answer with verifiable citations</p>
        </div>
      </div>
    );
  }

  if (!answer) {
    return (
      <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-8 shadow-xl text-center py-16 space-y-3">
        <div className="inline-flex p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-500">
          <ShieldCheck className="w-6 h-6 text-slate-500" />
        </div>
        <p className="text-sm font-medium text-slate-400">Ready for Enterprise Policy Query</p>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Submit a question above to generate an AI response backed by real document excerpts and citations.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
      {/* Status Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          {answer.is_sufficient ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-950/80 text-emerald-300 text-xs font-semibold rounded-full border border-emerald-800/60">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Grounded & Verified
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-950/80 text-amber-300 text-xs font-semibold rounded-full border border-amber-800/60">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Evidence Insufficient
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono">
          <span className="text-slate-400">Confidence:</span>
          <span className="text-cyan-400 font-bold">{(answer.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Answer Body */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
          Verified Answer
        </h3>
        <div className="p-5 rounded-xl bg-slate-950 border border-slate-800/80 text-slate-200 text-sm sm:text-base leading-relaxed whitespace-pre-line font-sans">
          {answer.text}
        </div>
      </div>

      {/* Supporting Citations */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
            Source Citations ({answer.citations.length})
          </h3>
          <span className="text-[11px] text-slate-500 font-mono">Click chunk to inspect evidence</span>
        </div>

        {answer.citations.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No source citations referenced for this response.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {answer.citations.map((cit, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedCitation(cit)}
                className="p-3.5 bg-slate-950/70 hover:bg-slate-950 border border-slate-800 hover:border-cyan-500/50 rounded-xl text-left transition group flex items-start justify-between gap-3 shadow-sm"
              >
                <div className="overflow-hidden">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-semibold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                      {cit.chunk_id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 italic font-sans">
                    "{cit.snippet}"
                  </p>
                </div>
                <div className="p-1 rounded-lg bg-slate-900 text-slate-500 group-hover:text-cyan-400 group-hover:bg-cyan-950/40 transition shrink-0 mt-0.5">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Citation Inspector Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-5">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-cyan-950 text-cyan-400 border border-cyan-800/50">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm font-mono">Citation Inspector</h4>
                  <p className="text-[11px] text-slate-400">Verifying evidence chunk integrity</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Stable Chunk ID
                </span>
                <span className="text-xs font-mono bg-slate-950 text-cyan-300 px-3 py-1.5 rounded-lg border border-slate-800 inline-block">
                  {selectedCitation.chunk_id}
                </span>
              </div>

              <div>
                <span className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Source Excerpt / Snippet
                </span>
                <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/30 text-xs sm:text-sm text-slate-200 italic leading-relaxed shadow-inner">
                  "{selectedCitation.snippet}"
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
