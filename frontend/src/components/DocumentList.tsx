import React from 'react';
import { DocumentSummary } from '../types/api';
import { FileCode, Layers, RefreshCw } from 'lucide-react';

interface DocumentListProps {
  documents: DocumentSummary[];
  loading: boolean;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, loading, onRefresh }) => {
  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <FileCode className="w-5 h-5 text-indigo-600" /> Ingested Documents
        </h2>
        <button
          onClick={onRefresh}
          className="text-slate-500 hover:text-indigo-600 p-1 rounded transition"
          title="Refresh document list"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-8 border border-dashed border-slate-200 rounded-lg bg-slate-50">
          <Layers className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-500">No documents indexed yet.</p>
          <p className="text-xs text-slate-400 mt-1">Upload a document above to start asking questions.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
          {documents.map((doc, idx) => (
            <div
              key={idx}
              className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between hover:bg-slate-100 transition"
            >
              <div className="overflow-hidden">
                <p className="text-sm font-medium text-slate-800 truncate">{doc.filename}</p>
                <p className="text-xs text-slate-500">
                  {doc.metadata?.file_type?.toUpperCase() || 'FILE'} • {doc.total_chunks} chunks
                </p>
              </div>
              <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full shrink-0">
                Indexed
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
