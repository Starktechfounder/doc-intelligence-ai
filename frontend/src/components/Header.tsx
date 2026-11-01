import React from 'react';
import type { HealthResponse } from '../types/api';
import { Shield, RefreshCw, Layers } from 'lucide-react';

interface HeaderProps {
  health: HealthResponse | null;
  loading: boolean;
  docCount: number;
  totalChunks: number;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  loading,
  docCount,
  totalChunks,
  onRefresh
}) => {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500/20 via-violet-500/20 to-cyan-400/30 border border-cyan-500/30 flex items-center justify-center shadow-lg shadow-cyan-500/10">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white font-mono">
                DOC<span className="text-cyan-400">INTELLIGENCE</span>
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                PRO
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Enterprise Policy Intelligence & Grounded Q&A
            </p>
          </div>
        </div>

        {/* Status metrics & actions */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Index Counter */}
          <div className="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Layers className="w-3.5 h-3.5 text-violet-400" />
              <span>{docCount} {docCount === 1 ? 'doc' : 'docs'}</span>
            </div>
            <span className="text-slate-700">•</span>
            <span className="text-slate-400">{totalChunks} chunks indexed</span>
          </div>

          {/* Connection status badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <div className="relative flex h-2 w-2">
              {isHealthy && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isHealthy ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
            </div>
            <span className="text-slate-300 font-mono text-[11px]">
              {isHealthy ? `API v${health?.version || '1.0'}` : 'Offline'}
            </span>
          </div>

          {/* Refresh connection button */}
          <button
            onClick={onRefresh}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white transition group focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
            title="Refresh API Connection"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : 'group-hover:rotate-45'} transition-transform duration-300`} />
          </button>
        </div>
      </div>
    </header>
  );
};
