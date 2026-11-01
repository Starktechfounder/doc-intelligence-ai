import React, { useState } from 'react';
import { Search, Loader2, HelpCircle, Sliders } from 'lucide-react';

interface QuestionFormProps {
  onSubmit: (query: string, top_k: number, min_score: number) => void;
  loading: boolean;
  disabled: boolean;
}

export const QuestionForm: React.FC<QuestionFormProps> = ({ onSubmit, loading, disabled }) => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(3);
  const [minScore, setMinScore] = useState(0.0);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query.trim(), topK, minScore);
  };

  const sampleQueries = [
    "What are the password requirements?",
    "How is multi-factor authentication enforced?",
    "What are the incident response procedures?"
  ];

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <Search className="w-5 h-5 text-indigo-600" /> Ask a Policy Question
        </h2>
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-xs text-slate-500 hover:text-indigo-600 flex items-center gap-1"
        >
          <Sliders className="w-3.5 h-3.5" />
          {showAdvanced ? 'Hide Settings' : 'Retrieval Settings'}
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your question about uploaded documents..."
            rows={3}
            disabled={disabled || loading}
            className="w-full p-3 border border-slate-300 rounded-lg text-sm text-slate-800 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-50 resize-none"
          />
        </div>

        {showAdvanced && (
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg grid grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-600 font-medium mb-1">
                Top Chunks (top_k): <span className="text-indigo-600 font-bold">{topK}</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full accent-indigo-600"
              />
            </div>
            <div>
              <label className="block text-slate-600 font-medium mb-1">
                Min Similarity Score: <span className="text-indigo-600 font-bold">{minScore.toFixed(2)}</span>
              </label>
              <input
                type="range"
                min="0.0"
                max="0.8"
                step="0.05"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full accent-indigo-600"
              />
            </div>
          </div>
        )}

        <div className="flex items-center justify-between gap-4">
          <div className="flex flex-wrap gap-1.5 items-center">
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <HelpCircle className="w-3 h-3" /> Quick questions:
            </span>
            {sampleQueries.map((q, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setQuery(q)}
                disabled={disabled || loading}
                className="text-xs px-2 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-600 rounded transition"
              >
                {q}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={disabled || loading || !query.trim()}
            className="py-2 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-medium rounded-lg shadow transition flex items-center gap-2 text-sm shrink-0"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Searching...
              </>
            ) : (
              'Get Answer'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
