import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentList } from './components/DocumentList';
import { QuestionForm } from './components/QuestionForm';
import { AnswerDisplay } from './components/AnswerDisplay';
import { api } from './api/client';
import { Answer, DocumentSummary, HealthResponse } from './types/api';
import './index.css';

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(false);
  const [appLoading, setAppLoading] = useState(false);

  const fetchAppData = useCallback(async () => {
    setAppLoading(true);
    try {
      const [h, docs] = await Promise.all([api.getHealth(), api.listDocuments()]);
      setHealth(h);
      setDocuments(docs);
    } catch (e) {
      console.error('Failed to sync app state', e);
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
    try {
      const res = await api.query(query, top_k, min_score);
      setAnswer(res);
    } catch (e) {
      console.error('Query failed', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-6">
        <Header health={health} loading={appLoading} onRefresh={fetchAppData} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <DocumentUpload onIngestSuccess={fetchAppData} />
            <DocumentList documents={documents} loading={appLoading} onRefresh={fetchAppData} />
          </div>

          <div className="lg:col-span-2 space-y-6">
            <QuestionForm onSubmit={handleQuery} loading={loading} disabled={documents.length === 0} />
            <AnswerDisplay answer={answer} loading={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
