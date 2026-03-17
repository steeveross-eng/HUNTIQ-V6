/**
 * BionicScoreBadge — Badge score consolidé avec anneau circulaire
 * Affiche le score écologique 0-100, label, et anneau progressif
 * Palette: bleu → vert → jaune → rouge
 * Conforme Steeve-MAX
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';

const getScoreConfig = (score) => {
  if (score >= 80) return { label: 'Optimal', color: '#DC2626', ring: '#DC2626', bg: 'rgba(220,38,38,0.12)' };
  if (score >= 60) return { label: 'Bon', color: '#F59E0B', ring: '#F59E0B', bg: 'rgba(245,158,11,0.12)' };
  if (score >= 40) return { label: 'Modéré', color: '#22C55E', ring: '#22C55E', bg: 'rgba(34,197,94,0.12)' };
  return { label: 'Faible', color: '#3B82F6', ring: '#3B82F6', bg: 'rgba(59,130,246,0.12)' };
};

export const BionicScoreBadge = ({ center, species = 'cerf', month = 10, compact = false }) => {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef(null);

  const fetchScore = useCallback(async () => {
    if (!center) return;
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    setLoading(true);

    const speciesMap = {
      orignal: 'ORIGNAL', chevreuil: 'CERF', ours_noir: 'OURS',
      dindon_sauvage: 'DINDON', wapiti: 'WAPITI', tous: 'CERF',
    };
    const sp = speciesMap[species] || 'CERF';
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    try {
      const res = await fetch(
        `${apiUrl}/api/v1/score-consolide/point?lat=${center.lat}&lng=${center.lng}&species=${sp}&month=${month}`,
        { signal: abortRef.current.signal }
      );
      if (res.ok) {
        const data = await res.json();
        setScore(data);
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error('[ScoreBadge]', e);
    }
    setLoading(false);
  }, [center, species, month]);

  useEffect(() => {
    fetchScore();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [fetchScore]);

  if (!score && !loading) return null;

  const val = score?.score || 0;
  const cfg = getScoreConfig(val);
  const pct = val / 100;
  const circumference = 2 * Math.PI * 16;
  const strokeDash = `${circumference * pct} ${circumference * (1 - pct)}`;

  if (compact) {
    return (
      <div
        className="flex items-center gap-1.5 px-2 py-1 rounded-md border transition-all"
        style={{ borderColor: `${cfg.color}40`, backgroundColor: cfg.bg }}
        data-testid="score-badge-compact"
      >
        {loading ? (
          <div className="w-4 h-4 rounded-full border-2 border-gray-500 border-t-transparent animate-spin" />
        ) : (
          <>
            <svg width="22" height="22" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="#374151" strokeWidth="2.5" />
              <circle
                cx="18" cy="18" r="16" fill="none"
                stroke={cfg.ring} strokeWidth="2.5" strokeLinecap="round"
                strokeDasharray={strokeDash}
                transform="rotate(-90 18 18)"
                style={{ transition: 'stroke-dasharray 0.6s ease-out' }}
              />
              <text x="18" y="20" textAnchor="middle" fill={cfg.color} fontSize="9" fontWeight="800">{Math.round(val)}</text>
            </svg>
            <span className="text-[9px] font-bold uppercase tracking-wider" style={{ color: cfg.color }}>{cfg.label}</span>
          </>
        )}
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all"
      style={{ borderColor: `${cfg.color}40`, backgroundColor: cfg.bg }}
      data-testid="score-badge"
    >
      {loading ? (
        <div className="w-6 h-6 rounded-full border-2 border-gray-500 border-t-transparent animate-spin" />
      ) : (
        <>
          <svg width="32" height="32" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="16" fill="none" stroke="#374151" strokeWidth="2" />
            <circle
              cx="18" cy="18" r="16" fill="none"
              stroke={cfg.ring} strokeWidth="2.5" strokeLinecap="round"
              strokeDasharray={strokeDash}
              transform="rotate(-90 18 18)"
              style={{ transition: 'stroke-dasharray 0.6s ease-out' }}
            />
            <text x="18" y="20.5" textAnchor="middle" fill={cfg.color} fontSize="10" fontWeight="800">{Math.round(val)}</text>
          </svg>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: cfg.color }}>{cfg.label}</span>
            <span className="text-[8px] text-gray-500">Score écologique</span>
          </div>
        </>
      )}
    </div>
  );
};
