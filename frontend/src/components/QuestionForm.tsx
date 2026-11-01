import React, { useState } from 'react';
import { Search, Loader2, Sparkles, SlidersHorizontal, CornerDownLeft } from 'lucide-react';

interface QuestionFormProps {
  onSubmit: (query: string, top_k: number, min_score: number) => void;
  loading: boolean;
  disabled: boolean;
}

export const QuestionForm: React.FC<QuestionFormProps> = ({ onSubmit, loading, disabled }) => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(3);
  const [minScore, setMinScore] = useState(0.0);
  const [showSettings, setShowSettings] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query.trim(), topK, minScore);
  };

  const sampleQuestions = [
    "What are the password length and complexity requirements?",
    "When is Multi-Factor Authentication (MFA) mandatory?",
    "How should security incidents and breaches be reported?"
  ];

  return (
    <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2 font-mono">
          <Search className="w-4 h-4 text-cyan-400" /> Policy Search & Q&A
        </h2>
        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 transition"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>{showSettings ? 'Hide Tuning' : 'Retrieval Tuning'}</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main query input */}
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                if (query.trim() && !disabled && !loading) {
                  onSubmit(query.trim(), topK, minScore);
                }
              }
            }}
            placeholder="Ask a question about security controls, audit policies, or compliance guidelines..."
            rows={3}
            disabled={disabled || loading}
            className="w-full rounded-xl bg-slate-950 border border-slate-800 p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 disabled:opacity-50 resize-none font-sans shadow-inner"
          />
          <div className="absolute bottom-3 right-3 flex items-center gap-2 text-[10px] text-slate-500 font-mono">
            <span>Ctrl + Enter to search</span>
            <CornerDownLeft className="w-3 h-3" />
          </div>
        </div>

        {/* Advanced Retrieval Settings Drawer */}
        {showSettings && (
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-slate-300 font-medium">Top Chunks (top_k)</span>
                <span className="font-mono font-bold text-cyan-400">{topK}</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full accent-cyan-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Number of source passages retrieved for context</span>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-slate-300 font-medium">Min Similarity Score</span>
                <span className="font-mono font-bold text-cyan-400">{minScore.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.8"
                step="0.05"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full accent-cyan-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">Relevance filter threshold</span>
            </div>
          </div>
        )}

        {/* Quick sample questions & Submit button */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-1">
          <div className="space-y-1.5 w-full sm:w-auto">
            <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono uppercase tracking-wide">
              <Sparkles className="w-3 h-3 text-violet-400" /> Suggested Prompts:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuery(q)}
                  disabled={disabled || loading}
                  className="text-xs px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 transition text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={disabled || loading || !query.trim()}
            className="w-full sm:w-auto py-3 px-6 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-semibold text-xs tracking-wider uppercase transition shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 shrink-0 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Querying RAG...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" /> Ask Policy AI
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
