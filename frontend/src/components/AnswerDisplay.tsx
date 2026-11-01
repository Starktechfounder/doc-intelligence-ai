import React, { useState } from 'react';
import { Answer, Citation } from '../types/api';
import { CheckCircle, AlertTriangle, Quote, FileText, ChevronRight, X } from 'lucide-react';

interface AnswerDisplayProps {
  answer: Answer | null;
  loading: boolean;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer, loading }) => {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm text-center py-12">
        <div className="inline-block p-3 bg-indigo-50 rounded-full text-indigo-600 mb-3 animate-bounce">
          <Quote className="w-6 h-6" />
        </div>
        <p className="text-sm font-medium text-slate-700">Searching indexed documents & generating grounded response...</p>
        <p className="text-xs text-slate-400 mt-1">Extracting citations and checking evidence validity</p>
      </div>
    );
  }

  if (!answer) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm text-center py-12">
        <Quote className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <p className="text-sm font-medium text-slate-500">No question asked yet.</p>
        <p className="text-xs text-slate-400 mt-1">Submit a question above to receive a grounded answer with citations.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
      {/* Status Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          {answer.is_sufficient ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded-full border border-emerald-200">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600" /> Evidence Sufficient
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 text-amber-800 text-xs font-semibold rounded-full border border-amber-200">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> Evidence Insufficient
            </span>
          )}
        </div>
        <div className="text-xs text-slate-500">
          Confidence Score: <span className="font-bold text-slate-700">{(answer.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Answer Body */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Grounded Answer</h3>
        <p className="text-sm text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
          {answer.text}
        </p>
      </div>

      {/* Citations List */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
          <span>Supporting Citations ({answer.citations.length})</span>
        </h3>

        {answer.citations.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No specific source citations provided.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {answer.citations.map((cit, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedCitation(cit)}
                className="p-3 bg-indigo-50/50 hover:bg-indigo-50 border border-indigo-100 rounded-lg text-left transition group flex items-start justify-between"
              >
                <div>
                  <span className="text-xs font-mono font-semibold text-indigo-700 block mb-1">
                    {cit.chunk_id}
                  </span>
                  <p className="text-xs text-slate-600 line-clamp-2 italic">
                    "{cit.snippet}"
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-indigo-400 group-hover:text-indigo-600 shrink-0 mt-0.5" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Citation Inspector Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-600" /> Citation Details
              </h4>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase block">Chunk ID</span>
                <span className="text-xs font-mono bg-slate-100 text-slate-800 px-2 py-1 rounded inline-block mt-0.5">
                  {selectedCitation.chunk_id}
                </span>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase block">Snippet</span>
                <p className="text-xs text-slate-800 bg-amber-50/60 border border-amber-100 p-3 rounded-lg italic mt-1 leading-relaxed">
                  "{selectedCitation.snippet}"
                </p>
              </div>
            </div>

            <div className="mt-5 text-right">
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
