/**
 * BCE4XIndicator — Indicateur temps reel BCE-4X dans le header territoire
 * Affiche: statut PASS/WARNING/FAIL, timestamp, validateurs, violations
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Shield, RefreshCw } from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';

const STATUS_STYLES = {
  PASS: { bg: 'bg-green-500/15', border: 'border-green-500/40', text: 'text-green-400', dot: 'bg-green-500' },
  PARTIAL: { bg: 'bg-yellow-500/15', border: 'border-yellow-500/40', text: 'text-yellow-400', dot: 'bg-yellow-500' },
  WARNING: { bg: 'bg-yellow-500/15', border: 'border-yellow-500/40', text: 'text-yellow-400', dot: 'bg-yellow-500' },
  FAIL: { bg: 'bg-red-500/15', border: 'border-red-500/40', text: 'text-red-400', dot: 'bg-red-500' },
  ERROR: { bg: 'bg-red-500/15', border: 'border-red-500/40', text: 'text-red-400', dot: 'bg-red-500' },
  LOADING: { bg: 'bg-gray-500/15', border: 'border-gray-500/40', text: 'text-gray-400', dot: 'bg-gray-500' },
};

const BCE4XIndicator = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API = process.env.REACT_APP_BACKEND_URL;

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/bce/validate`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [API]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const status = loading ? 'LOADING' : (data?.overall_status || 'ERROR');
  const style = STATUS_STYLES[status] || STATUS_STYLES.ERROR;
  const summary = data?.summary || {};
  const timestamp = data?.timestamp;

  const violations = {
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
  };
  if (data?.validators) {
    for (const v of data.validators) {
      if (v.status === 'FAIL') {
        const errors = v.errors || [];
        if (errors.some(e => typeof e === 'string' && (e.includes('spatial') || e.includes('water') || e.includes('scoring') || e.includes('corridor')))) {
          violations.HIGH++;
        } else {
          violations.MEDIUM++;
        }
      } else if (v.status === 'SKIP') {
        violations.LOW++;
      }
    }
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          className={`h-9 px-3 flex items-center gap-2 rounded-lg border ${style.bg} ${style.border} transition-all hover:opacity-90`}
          data-testid="bce4x-indicator-btn"
          title="Statut BCE-4X"
        >
          <Shield className={`h-4 w-4 ${style.text}`} />
          <div className={`w-2 h-2 rounded-full ${style.dot} ${loading ? 'animate-pulse' : ''}`} />
          <span className={`text-[10px] font-bold uppercase tracking-wider ${style.text}`}>
            BCE-4X {loading ? '...' : status}
          </span>
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" sideOffset={8} className="w-80 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-0 shadow-xl shadow-black/40">
        <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className={`h-3.5 w-3.5 ${style.text}`} />
            <span className="text-xs font-semibold text-white">BCE-4X Compliance</span>
          </div>
          <button onClick={fetchStatus} className="text-gray-500 hover:text-white transition-colors" data-testid="bce4x-refresh-btn">
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        <div className="p-3 space-y-3">
          {/* Status Badge */}
          <div className={`flex items-center justify-between rounded-lg px-3 py-2 ${style.bg} border ${style.border}`}>
            <span className="text-xs text-gray-300 font-medium">Statut global</span>
            <span className={`text-sm font-bold ${style.text}`} data-testid="bce4x-status">{loading ? 'Chargement...' : status}</span>
          </div>

          {/* Timestamp */}
          {timestamp && (
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500">Derniere validation</span>
              <span className="text-gray-300 font-mono" data-testid="bce4x-timestamp">
                {new Date(timestamp).toLocaleString('fr-CA', { dateStyle: 'short', timeStyle: 'medium' })}
              </span>
            </div>
          )}

          {/* Validators */}
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-gray-500">Validateurs actifs</span>
            <span className="text-white font-bold" data-testid="bce4x-validators-count">{summary.total_validators || '—'}</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-gray-500">Checks passes</span>
            <span className="text-green-400 font-bold">{summary.checks_passed || 0} / {summary.total_checks || 0}</span>
          </div>

          {/* Violations */}
          <div className="space-y-1 pt-2 border-t border-gray-800">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Violations</span>
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-red-500/10 border border-red-500/20 rounded px-2 py-1 text-center">
                <div className="text-sm font-bold text-red-400" data-testid="bce4x-high-count">{violations.HIGH}</div>
                <div className="text-[9px] text-red-400/70">HIGH</div>
              </div>
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded px-2 py-1 text-center">
                <div className="text-sm font-bold text-yellow-400" data-testid="bce4x-medium-count">{violations.MEDIUM}</div>
                <div className="text-[9px] text-yellow-400/70">MEDIUM</div>
              </div>
              <div className="bg-gray-500/10 border border-gray-500/20 rounded px-2 py-1 text-center">
                <div className="text-sm font-bold text-gray-400" data-testid="bce4x-low-count">{violations.LOW}</div>
                <div className="text-[9px] text-gray-400/70">LOW</div>
              </div>
            </div>
          </div>

          {/* Error display */}
          {error && (
            <div className="text-[10px] text-red-400 bg-red-500/10 rounded p-2">
              Erreur: {error}
            </div>
          )}

          {/* Failed validators list */}
          {data?.validators?.filter(v => v.status === 'FAIL').length > 0 && (
            <div className="space-y-1 pt-2 border-t border-gray-800">
              <span className="text-[10px] text-red-400 uppercase tracking-wider font-bold">Validateurs en echec</span>
              {data.validators.filter(v => v.status === 'FAIL').map((v, i) => (
                <div key={i} className="text-[10px] text-red-300 bg-red-500/5 rounded px-2 py-1">
                  {v.name}
                </div>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default BCE4XIndicator;
