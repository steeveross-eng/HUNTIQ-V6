/**
 * SeasonalConditionsWidget.jsx
 * PHASE E — Mini-dashboard Conditions Saisonnières
 *
 * Composant de rendu pur. 0 logique, 0 calcul.
 * Appelle GET /api/v1/bionic/seasonal-conditions?lat=X&lng=Y
 * Affiche: météo, phénologie, pression de chasse, score global.
 */

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Badge } from "@/components/ui/badge";
import { Loader2, Thermometer, Wind, Droplets, Gauge, Sun, TreeDeciduous, Crosshair, ChevronDown, ChevronUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const RATING_COLORS = {
  excellent: "text-emerald-400 border-emerald-500/40 bg-emerald-900/30",
  bon: "text-green-400 border-green-500/40 bg-green-900/30",
  moyen: "text-amber-400 border-amber-500/40 bg-amber-900/30",
  defavorable: "text-red-400 border-red-500/40 bg-red-900/30",
};

const CONDITION_ICONS = {
  degaje: "Degaje",
  partiellement_nuageux: "Nuageux",
  nuageux: "Couvert",
  brouillard: "Brouillard",
  pluie: "Pluie",
  neige: "Neige",
};

const RUT_LABELS = {
  pre_rut: "Pre-rut",
  rut_actif: "Rut actif",
  post_rut: "Post-rut",
  inactif: "Inactif",
};

export default function SeasonalConditionsWidget({ lat, lng }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const lastKeyRef = useRef(null);

  useEffect(() => {
    if (!lat || !lng) return;
    const key = `${lat.toFixed(2)}_${lng.toFixed(2)}`;
    if (lastKeyRef.current === key && data) return;
    lastKeyRef.current = key;

    setLoading(true);
    axios.get(`${BACKEND_URL}/api/v1/bionic/seasonal-conditions`, {
      params: { lat, lng },
      timeout: 10000,
    })
      .then((res) => {
        setData(res.data);
      })
      .catch((err) => {
        console.warn("[Seasonal] fetch error:", err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [lat, lng, data]);

  if (loading) {
    return (
      <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700" data-testid="seasonal-widget-loading">
        <div className="flex items-center gap-2 text-[10px] text-gray-400">
          <Loader2 className="h-3 w-3 animate-spin" />
          Conditions saisonnieres...
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { meteo, phenologie, pression_chasse, score } = data;
  const ratingClass = RATING_COLORS[score?.rating] || RATING_COLORS.moyen;

  return (
    <div className={`rounded-lg p-3 border ${ratingClass}`} data-testid="seasonal-widget">
      {/* Header with score */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between mb-2"
        data-testid="seasonal-toggle"
      >
        <div className="flex items-center gap-2">
          <Sun className="h-4 w-4" />
          <span className="text-xs font-semibold">Conditions</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Badge className="bg-black/60 text-[10px] px-1.5 py-0.5 font-mono" data-testid="seasonal-score">
            {score?.global}/100
          </Badge>
          {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </div>
      </button>

      {/* Compact summary — always visible */}
      <div className="grid grid-cols-4 gap-1 text-center" data-testid="seasonal-summary">
        <div title="Temperature">
          <Thermometer className="h-3 w-3 mx-auto mb-0.5 opacity-60" />
          <div className="text-[10px] font-mono">{meteo?.temperature_c}°</div>
        </div>
        <div title="Vent">
          <Wind className="h-3 w-3 mx-auto mb-0.5 opacity-60" />
          <div className="text-[10px] font-mono">{meteo?.vent_kmh} km/h</div>
        </div>
        <div title="Precipitations">
          <Droplets className="h-3 w-3 mx-auto mb-0.5 opacity-60" />
          <div className="text-[10px] font-mono">{meteo?.precipitations_mm} mm</div>
        </div>
        <div title="Pression">
          <Gauge className="h-3 w-3 mx-auto mb-0.5 opacity-60" />
          <div className="text-[10px] font-mono">{meteo?.pression_hpa}</div>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="mt-2 pt-2 border-t border-white/10 space-y-2" data-testid="seasonal-details">
          {/* Meteo detail */}
          <div className="space-y-1">
            <div className="text-[10px] text-gray-300 font-medium flex items-center gap-1">
              <Thermometer className="h-3 w-3" /> Meteo
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px]">
              <span className="text-gray-500">Condition</span>
              <span className="text-right">{CONDITION_ICONS[meteo?.condition] || meteo?.condition}</span>
              <span className="text-gray-500">Ressenti</span>
              <span className="text-right">{meteo?.ressenti_c}°C</span>
              <span className="text-gray-500">Humidite</span>
              <span className="text-right">{meteo?.humidite_pct}%</span>
              <span className="text-gray-500">Pression</span>
              <span className="text-right">{meteo?.pression_hpa} hPa ({meteo?.pression_tendance})</span>
            </div>
          </div>

          {/* Phenologie */}
          <div className="space-y-1">
            <div className="text-[10px] text-gray-300 font-medium flex items-center gap-1">
              <TreeDeciduous className="h-3 w-3" /> Phenologie
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px]">
              <span className="text-gray-500">Saison</span>
              <span className="text-right capitalize">{phenologie?.saison}</span>
              <span className="text-gray-500">Phase</span>
              <span className="text-right">{phenologie?.phase?.label}</span>
              <span className="text-gray-500">Activite veg.</span>
              <span className="text-right">{Math.round((phenologie?.phase?.vegetation_activity || 0) * 100)}%</span>
              <span className="text-gray-500">Duree jour</span>
              <span className="text-right">{phenologie?.duree_jour_h}h</span>
              <span className="text-gray-500">Lever</span>
              <span className="text-right">{phenologie?.lever_soleil}</span>
              <span className="text-gray-500">Coucher</span>
              <span className="text-right">{phenologie?.coucher_soleil}</span>
            </div>
            {/* Rut status */}
            {phenologie?.rut && Object.entries(phenologie.rut).map(([sp, r]) => (
              <div key={sp} className="flex items-center justify-between text-[9px]">
                <span className="text-gray-500 capitalize">{sp} rut</span>
                <Badge className={`text-[8px] px-1 py-0 ${r.intensity > 0.5 ? 'bg-red-900/40 text-red-300 border-red-500/30' : 'bg-gray-800 text-gray-400 border-gray-600'}`}>
                  {RUT_LABELS[r.status] || r.status} ({Math.round(r.intensity * 100)}%)
                </Badge>
              </div>
            ))}
          </div>

          {/* Pression de chasse */}
          <div className="space-y-1">
            <div className="text-[10px] text-gray-300 font-medium flex items-center gap-1">
              <Crosshair className="h-3 w-3" /> Pression de chasse
            </div>
            <div className="flex items-center justify-between text-[9px]">
              <span className="text-gray-500">Intensite</span>
              <span>{pression_chasse?.label}</span>
            </div>
            {pression_chasse?.active_seasons?.length > 0 ? (
              pression_chasse.active_seasons.map((s) => (
                <div key={s.id} className="flex items-center justify-between text-[9px]">
                  <span className="text-gray-500 truncate max-w-[80px]">{s.label}</span>
                  <span className="text-amber-300">{s.days_remaining}j restants</span>
                </div>
              ))
            ) : (
              <div className="text-[9px] text-gray-500">Aucune saison active</div>
            )}
          </div>

          {/* Score breakdown */}
          <div className="space-y-1">
            <div className="text-[10px] text-gray-300 font-medium">Score detail</div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[9px]">
              <span className="text-gray-500">Meteo</span>
              <span className="text-right">{score?.detail?.meteo}/100</span>
              <span className="text-gray-500">Phenologie</span>
              <span className="text-right">{score?.detail?.phenologie}/40</span>
              <span className="text-gray-500">Rut</span>
              <span className="text-right">{score?.detail?.rut}/30</span>
              <span className="text-gray-500">Pression faible</span>
              <span className="text-right">{score?.detail?.faible_pression}/30</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
