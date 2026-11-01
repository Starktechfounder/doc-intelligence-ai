import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { Hero3D } from './components/Hero3D';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentList } from './components/DocumentList';
import { QuestionForm } from './components/QuestionForm';
import { AnswerDisplay } from './components/AnswerDisplay';
import { api } from './api/client';
import type { Answer, DocumentSummary, HealthResponse } from './types/api';
import { AlertCircle } from 'lucide-react';
import './index.css';

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(false);
  const [appLoading, setAppLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const fetchAppData = useCallback(async () => {
    setAppLoading(true);
    setApiError(null);
    try {
      const [h, docs] = await Promise.all([
        api.getHealth().catch(() => null),
        api.listDocuments().catch(() => [])
      ]);
      setHealth(h);
      setDocuments(docs || []);
      if (!h) {
        setApiError('Unable to connect to FastAPI backend on port 8000. Ensure the backend service is running.');
      }
    } catch (e: any) {
      setApiError(e.message || 'Error fetching system status');
    } finally {
      setAppLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAppData();
  }, [fetchAppData]);

  const handleQuery = async (query: string, top_k: number, min_score: number) => {
    setLoading(true);
    setAnswer(null);
    setApiError(null);
    try {
      const res = await api.query(query, top_k, min_score);
      setAnswer(res);
    } catch (e: any) {
      setApiError(e.message || 'Failed to generate answer');
    } finally {
      setLoading(false);
    }
  };

  const totalChunks = documents.reduce((acc, doc) => acc + (doc.total_chunks || 0), 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Header
        health={health}
        loading={appLoading}
        docCount={documents.length}
        totalChunks={totalChunks}
        onRefresh={fetchAppData}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        {/* Offline / Error Alert */}
        {apiError && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs sm:text-sm flex items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{apiError}</span>
            </div>
            <button
              onClick={fetchAppData}
              className="px-3 py-1 rounded-lg bg-rose-900/60 hover:bg-rose-900 text-rose-200 text-xs font-mono uppercase tracking-wider transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* 3D Visual Hero */}
        <Hero3D />

        {/* Dashboard 2-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Document Ingestion & Knowledge Base */}
          <div className="lg:col-span-4 space-y-6">
            <DocumentUpload onIngestSuccess={fetchAppData} />
            <DocumentList
              documents={documents}
              loading={appLoading}
              onRefresh={fetchAppData}
            />
          </div>

          {/* Right Column: Query Search & Grounded Answer */}
          <div className="lg:col-span-8 space-y-6">
            <QuestionForm
              onSubmit={handleQuery}
              loading={loading}
              disabled={documents.length === 0}
            />
            <AnswerDisplay answer={answer} loading={loading} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 mt-12 text-center text-xs text-slate-500 font-mono">
        <p>Enterprise Policy Document Intelligence AI • Production-Grade Verifiable RAG</p>
      </footer>
    </div>
  );
}

export default App;
