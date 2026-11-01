import React from 'react';
import { HealthResponse } from '../types/api';
import { ShieldCheck, Server, RefreshCw } from 'lucide-react';

interface HeaderProps {
  health: HealthResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, loading, onRefresh }) => {
  return (
    <header className="bg-slate-900 text-white p-4 shadow-md flex justify-between items-center rounded-b-lg">
      <div className="flex items-center space-x-3">
        <ShieldCheck className="w-8 h-8 text-indigo-400" />
        <div>
          <h1 className="text-xl font-bold tracking-tight">Doc Intelligence AI</h1>
          <p className="text-xs text-slate-400">Enterprise Policy Q&A & Document Intelligence System</p>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700">
          <Server className={`w-4 h-4 ${health?.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`} />
          <span className="text-xs text-slate-300">
            {health ? `v${health.version} - ${health.status}` : 'Disconnected'}
          </span>
        </div>
        <button
          onClick={onRefresh}
          className="p-1.5 hover:bg-slate-800 rounded-full text-slate-300 hover:text-white transition"
          title="Refresh connection"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </header>
  );
};
