/**
 * CompareWidget — BIONIC V8.3.A
 * Comparaison côte à côte de 2-3 waypoints.
 * Affiche: scores, zones, corridors, météo, pression anthropique.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { X, ChevronDown, ChevronUp, MapPin, Thermometer, Wind, Droplets, TreePine, Target, ArrowRight, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const LAYER_LABELS = {
  habitats: 'Habitats', alimentation: 'Alimentation',
  repos: 'Repos', rut: 'Rut', corridors: 'Corridors',
};

const INTENSITY_COLORS = {
  forte: '#22c55e', modérée: '#f59e0b', faible: '#6b7280', aucun: '#374151',
};

const PRESSURE_COLORS = {
  faible: '#22c55e', modérée: '#f59e0b', élevée: '#ef4444',
};

function ScoreBar({ score, maxScore = 100, color = '#22c55e' }) {
  const pct = Math.min(100, (score / maxScore) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-mono text-gray-300 w-8 text-right">{score}</span>
    </div>
  );
}

function Section({ title, icon: Icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-t border-gray-800/50">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-800/30 transition-colors" data-testid={`section-${title.toLowerCase()}`}>
        {Icon && <Icon className="h-3 w-3 text-gray-500" />}
        <span className="text-[10px] text-gray-400 uppercase tracking-wider font-medium flex-1 text-left">{title}</span>
        {open ? <ChevronUp className="h-3 w-3 text-gray-600" /> : <ChevronDown className="h-3 w-3 text-gray-600" />}
      </button>
      {open && <div className="px-3 pb-3">{children}</div>}
    </div>
  );
}

function WaypointColumn({ data }) {
  if (data.error) {
    return (
      <div className="flex-1 min-w-0 bg-[#0d0d16] rounded-lg border border-red-500/20 p-3">
        <div className="text-xs text-red-400">Erreur: {data.error}</div>
      </div>
    );
  }

  const wp = data.waypoint;
  const scores = data.scores || {};
  const zones = data.zones || {};
  const corridors = data.corridors || {};
  const weather = data.weather || {};
  const influence = data.weather_influence || {};
  const pressure = data.anthropic_pressure || {};
  const globalScore = scores.global || 0;

  const scoreColor = globalScore > 70 ? '#22c55e' : globalScore > 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex-1 min-w-0 bg-[#0d0d16] rounded-lg border border-[#1a1a2e] overflow-hidden" data-testid={`compare-column-${wp.id}`}>
      {/* Header */}
      <div className="p-3 bg-gradient-to-r from-[#111118] to-[#0d0d16] border-b border-[#1a1a2e]">
        <div className="flex items-center gap-2 mb-1">
          <MapPin className="h-3.5 w-3.5 text-cyan-400 flex-shrink-0" />
          <span className="text-sm font-semibold text-white truncate">{wp.name}</span>
        </div>
        <div className="text-[9px] text-gray-500">{wp.lat?.toFixed(4)}, {wp.lng?.toFixed(4)}</div>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-2xl font-bold" style={{ color: scoreColor }}>{globalScore}</span>
          <span className="text-xs text-gray-500">/100</span>
        </div>
      </div>

      {/* Scores par catégorie */}
      <Section title="Scores" icon={Target} defaultOpen={true}>
        <div className="space-y-2">
          {Object.entries(scores.by_category || {}).map(([cat, score]) => (
            <div key={cat}>
              <div className="text-[9px] text-gray-500 mb-0.5">{LAYER_LABELS[cat] || cat}</div>
              <ScoreBar score={score} color={score > 70 ? '#22c55e' : score > 40 ? '#f59e0b' : '#ef4444'} />
            </div>
          ))}
        </div>
      </Section>

      {/* Zones */}
      <Section title="Zones" icon={TreePine} defaultOpen={true}>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <div className="text-lg font-bold text-green-400">{zones.total || 0}</div>
            <div className="text-[8px] text-gray-500">zones valides</div>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-500">{zones.rejected || 0}</div>
            <div className="text-[8px] text-gray-500">rejetées</div>
          </div>
        </div>
        {zones.by_layer && Object.entries(zones.by_layer).length > 0 && (
          <div className="mt-2 space-y-1">
            {Object.entries(zones.by_layer).map(([layer, count]) => (
              <div key={layer} className="flex items-center justify-between">
                <span className="text-[8px] text-gray-500">{LAYER_LABELS[layer] || layer}</span>
                <span className="text-[9px] text-gray-300 font-mono">{count}</span>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Corridors */}
      <Section title="Corridors" icon={ArrowRight} defaultOpen={true}>
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-cyan-400">{corridors.count || 0}</span>
          <span
            className="text-[9px] px-2 py-0.5 rounded-full font-semibold"
            style={{
              backgroundColor: `${INTENSITY_COLORS[corridors.intensity] || '#374151'}20`,
              color: INTENSITY_COLORS[corridors.intensity] || '#6b7280',
            }}
          >
            {corridors.intensity || 'aucun'}
          </span>
        </div>
      </Section>

      {/* Météo */}
      <Section title="Météo" icon={Thermometer} defaultOpen={true}>
        {weather.temperature_c != null ? (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-gray-500 flex items-center gap-1"><Thermometer className="h-2.5 w-2.5" />Temp</span>
              <span className="text-xs text-gray-300 font-mono">{Math.round(weather.temperature_c)}°C</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-gray-500 flex items-center gap-1"><Wind className="h-2.5 w-2.5" />Vent</span>
              <span className="text-xs text-gray-300 font-mono">{Math.round(weather.wind_speed_kmh || 0)} km/h</span>
            </div>
            {weather.wind_gust_kmh > 0 && (
              <div className="flex items-center justify-between">
                <span className="text-[9px] text-gray-500">Rafales</span>
                <span className="text-xs text-gray-300 font-mono">{Math.round(weather.wind_gust_kmh)} km/h</span>
              </div>
            )}
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-gray-500 flex items-center gap-1"><Droplets className="h-2.5 w-2.5" />Précip.</span>
              <span className="text-xs text-gray-300 font-mono">{weather.precipitation_1h_mm || 0} mm</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[9px] text-gray-500">Condition</span>
              <span className="text-[9px] text-gray-400 italic">{weather.condition_detail || weather.condition || '—'}</span>
            </div>
            {/* Influence multipliers */}
            {influence && Object.keys(influence).length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-800/50">
                <div className="text-[8px] text-gray-600 mb-1">Influence scoring</div>
                {Object.entries(influence).map(([cat, mult]) => (
                  <div key={cat} className="flex items-center gap-1.5">
                    <span className="text-[7px] text-gray-500 w-14 truncate">{LAYER_LABELS[cat] || cat}</span>
                    <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{
                        width: `${Math.min(100, (mult / 1.3) * 100)}%`,
                        backgroundColor: mult > 1.05 ? '#22c55e' : mult < 0.95 ? '#ef4444' : '#4b5563',
                      }} />
                    </div>
                    <span className={`text-[7px] font-mono ${mult > 1.0 ? 'text-green-400' : mult < 1.0 ? 'text-red-400' : 'text-gray-500'}`}>
                      {mult > 1.0 ? '+' : ''}{((mult - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="text-[9px] text-gray-600 italic">Météo indisponible</div>
        )}
      </Section>

      {/* Pression anthropique */}
      <Section title="Pression" icon={MapPin} defaultOpen={false}>
        <div className="flex items-center gap-2">
          <span
            className="text-[10px] px-2 py-0.5 rounded-full font-semibold"
            style={{
              backgroundColor: `${PRESSURE_COLORS[pressure.level] || '#374151'}20`,
              color: PRESSURE_COLORS[pressure.level] || '#6b7280',
            }}
          >
            {pressure.level || 'inconnue'}
          </span>
          <span className="text-[8px] text-gray-500">{pressure.rejections || 0} rejets anthropiques</span>
        </div>
      </Section>

      {/* Footer computation time */}
      <div className="px-3 py-1.5 border-t border-gray-800/30 text-[7px] text-gray-700">
        Calculé en {data.computation_ms || 0}ms
      </div>
    </div>
  );
}

export default function CompareWidget({ waypoints, onClose }) {
  const [compareData, setCompareData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchComparison = useCallback(async (wps) => {
    if (!wps || wps.length < 2) return;
    setLoading(true);
    setError(null);
    try {
      const body = {
        waypoints: wps.map(wp => ({
          id: wp.id,
          name: wp.name,
          lat: wp.lat || wp.latitude,
          lng: wp.lng || wp.longitude,
        })),
      };
      const res = await fetch(`${API}/api/v1/compare/waypoints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setCompareData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (waypoints && waypoints.length >= 2) {
      fetchComparison(waypoints);
    }
  }, [waypoints, fetchComparison]);

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="compare-widget-overlay">
      <div className="bg-[#080810] border border-[#1a1a2e] rounded-xl shadow-2xl w-[95vw] max-w-[1200px] max-h-[90vh] overflow-hidden flex flex-col" data-testid="compare-widget">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#1a1a2e] bg-[#0d0d16]">
          <div>
            <h2 className="text-sm font-semibold text-white">Comparaison de waypoints</h2>
            <p className="text-[9px] text-gray-500 mt-0.5">
              {waypoints?.length || 0} waypoints — Pipeline V7 + Météo V8.3
            </p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-800/50 transition-colors" data-testid="compare-close-btn">
            <X className="h-4 w-4 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3" data-testid="compare-loading">
              <Loader2 className="h-6 w-6 text-cyan-400 animate-spin" />
              <span className="text-xs text-gray-400">Analyse comparative en cours...</span>
            </div>
          ) : error ? (
            <div className="text-center py-16 text-xs text-red-400" data-testid="compare-error">Erreur: {error}</div>
          ) : compareData ? (
            <div className="flex gap-3" data-testid="compare-columns">
              {compareData.comparison.map((data, i) => (
                <WaypointColumn key={data.waypoint?.id || i} data={data} />
              ))}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        {compareData && (
          <div className="px-4 py-2 border-t border-[#1a1a2e] bg-[#0d0d16] flex items-center justify-between">
            <span className="text-[8px] text-gray-600">
              Calcul total: {compareData.total_computation_ms}ms
            </span>
            <span className="text-[8px] text-gray-600">
              BIONIC V8.3.A — Compare Engine
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
