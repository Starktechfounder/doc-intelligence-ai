import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, ArrowUpRight } from 'lucide-react';

interface DocumentUploadProps {
  onIngestSuccess: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onIngestSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selected: File) => {
    const ext = selected.name.split('.').pop()?.toLowerCase();
    if (!['txt', 'md', 'pdf'].includes(ext || '')) {
      setStatusMsg({ type: 'error', text: 'Unsupported format. Allowed: .pdf, .md, .txt' });
      setFile(null);
      return;
    }

    if (selected.size > 10 * 1024 * 1024) {
      setStatusMsg({ type: 'error', text: 'File exceeds maximum limit of 10MB.' });
      setFile(null);
      return;
    }

    setFile(selected);
    setStatusMsg(null);
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
        text: `Indexed "${data.filename}" (${data.chunks_indexed} chunks)`
      });
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      onIngestSuccess();
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Ingestion failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2 font-mono">
          <UploadCloud className="w-4 h-4 text-cyan-400" /> Ingest Policy Document
        </h2>
        <span className="text-[11px] text-slate-500 font-mono">MAX 10MB</span>
      </div>

      <form onSubmit={handleUpload} className="space-y-4">
        {/* Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all duration-200 ${
            dragActive
              ? 'border-cyan-400 bg-cyan-950/20'
              : file
              ? 'border-violet-500/60 bg-violet-950/20'
              : 'border-slate-800 hover:border-slate-700 bg-slate-950/50 hover:bg-slate-950'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center space-y-2">
            <div className={`p-2.5 rounded-full ${file ? 'bg-violet-950 text-violet-400' : 'bg-slate-800 text-slate-400'}`}>
              <FileText className="w-6 h-6" />
            </div>

            {file ? (
              <div>
                <p className="text-xs font-semibold text-slate-200 truncate max-w-[220px]">
                  {file.name}
                </p>
                <p className="text-[10px] text-slate-400 font-mono">
                  {(file.size / 1024).toFixed(1)} KB • Click to change
                </p>
              </div>
            ) : (
              <div>
                <p className="text-xs font-medium text-slate-300">
                  Drop file here, or <span className="text-cyan-400 underline decoration-cyan-400/40">browse</span>
                </p>
                <div className="flex items-center justify-center gap-1.5 mt-2">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono">PDF</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono">MARKDOWN</span>
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono">TXT</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Status Message */}
        {statusMsg && (
          <div
            className={`p-3 rounded-lg text-xs flex items-center gap-2 border font-medium ${
              statusMsg.type === 'success'
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60'
                : 'bg-rose-950/40 text-rose-300 border-rose-800/60'
            }`}
          >
            {statusMsg.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span className="text-[11px] leading-tight">{statusMsg.text}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!file || loading}
          className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-medium text-xs tracking-wide uppercase transition shadow-lg shadow-cyan-500/10 flex items-center justify-center gap-2 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
        >
          {loading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Ingesting & Chunking...
            </>
          ) : (
            <>
              Process & Index Document <ArrowUpRight className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
