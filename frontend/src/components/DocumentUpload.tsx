import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface DocumentUploadProps {
  onIngestSuccess: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onIngestSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 10 * 1024 * 1024) {
        setStatusMsg({ type: 'error', text: 'File size exceeds maximum 10MB limit.' });
        setFile(null);
        return;
      }
      setFile(selected);
      setStatusMsg(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setStatusMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const res = await fetch(`${API_BASE}/ingest/file`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to ingest file');
      }

      const data = await res.json();
      setStatusMsg({
        type: 'success',
        text: `Successfully indexed ${data.filename} (${data.chunks_indexed} chunks)`
      });
      setFile(null);
      onIngestSuccess();
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800 mb-2 flex items-center gap-2">
        <Upload className="w-5 h-5 text-indigo-600" /> Upload Document
      </h2>
      <p className="text-xs text-slate-500 mb-4">
        Supported formats: .txt, .md, .pdf (Max size: 10MB)
      </p>

      <form onSubmit={handleUpload} className="space-y-4">
        <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-indigo-400 transition bg-slate-50">
          <input
            type="file"
            accept=".txt,.md,.pdf"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
            <FileText className="w-10 h-10 text-slate-400 mb-2" />
            <span className="text-sm font-medium text-slate-700">
              {file ? file.name : 'Click to choose or drag file here'}
            </span>
            <span className="text-xs text-slate-400 mt-1">
              {file ? `${(file.size / 1024).toFixed(1)} KB` : 'PDF, Markdown, or Plain Text'}
            </span>
          </label>
        </div>

        {statusMsg && (
          <div className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
            statusMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
          }`}>
            {statusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || loading}
          className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-medium rounded-lg shadow transition flex items-center justify-center gap-2 text-sm"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Ingesting & Chunking...
            </>
          ) : (
            'Ingest Document'
          )}
        </button>
      </form>
    </div>
  );
};
