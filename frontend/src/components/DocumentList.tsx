import React from 'react';
import type { DocumentSummary } from '../types/api';
import { FileCode, Layers, RefreshCw, Database } from 'lucide-react';

interface DocumentListProps {
  documents: DocumentSummary[];
  loading: boolean;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, loading, onRefresh }) => {
  return (
    <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2 font-mono">
          <Database className="w-4 h-4 text-violet-400" /> Knowledge Base
        </h2>
        <button
          onClick={onRefresh}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition focus:outline-none focus:ring-1 focus:ring-cyan-500"
          title="Refresh index list"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-violet-400' : ''}`} />
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-6 border border-dashed border-slate-800 rounded-xl bg-slate-950/40">
          <Layers className="w-6 h-6 text-slate-600 mx-auto mb-2" />
          <p className="text-xs font-medium text-slate-400">No documents indexed</p>
          <p className="text-[11px] text-slate-500 mt-0.5">Upload a file above to populate the vector store</p>
        </div>
      ) : (
        <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
          {documents.map((doc, idx) => (
            <div
              key={idx}
              className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg flex items-center justify-between hover:border-slate-700 transition"
            >
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="p-1.5 rounded bg-violet-950/60 text-violet-400 border border-violet-800/40 shrink-0">
                  <FileCode className="w-3.5 h-3.5" />
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs font-medium text-slate-200 truncate">{doc.filename}</p>
                  <p className="text-[10px] text-slate-500 font-mono">
                    {doc.total_chunks} {doc.total_chunks === 1 ? 'chunk' : 'chunks'} indexed
                  </p>
                </div>
              </div>

              <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 text-[10px] font-mono shrink-0">
                ACTIVE
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
