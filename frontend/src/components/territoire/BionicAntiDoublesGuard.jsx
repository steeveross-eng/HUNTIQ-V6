/**
 * BionicAntiDoublesGuard.jsx
 * 
 * BIONIC V5 300% — Protection anti-doublons ISOLÉE
 * 
 * RÔLE :
 *   1. Supprime TOUS les tooltips/popups parasites via injection CSS
 *   2. Centralise la détection de clic sur zone via ray-casting
 *   3. Déclenche exclusivement onZoneClick() pour le panneau diagnostique
 * 
 * CONTRAINTES RESPECTÉES :
 *   - AUCUNE modification aux modules protégés
 *   - Composant ISOLÉ, CONFINÉ et RÉVERSIBLE
 *   - Suppression CSS auto-nettoyée au démontage
 *   - Ray-casting point-in-polygon sans dépendance externe
 */

import { useEffect, useCallback, useRef } from 'react';
import { useMapEvents } from 'react-leaflet';

const STYLE_ID = 'bionic-anti-doubles-css';

const SUPPRESSION_CSS = `
/* STEVE-MAX: Anti-Doublons CSS — tooltips BIONIC uniquement */
/* BCE-4X-UI-004: Aucune suppression globale des panneaux Leaflet */
.bionic-smart-tooltip {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}
.bionic-smart-tooltip-arrow {
  display: none !important;
}
/* STEVE-MAX: Zone Hover Premium Effect */
.leaflet-overlay-pane path.leaflet-interactive {
  transition: stroke-width 120ms ease-out, filter 120ms ease-out !important;
}
.leaflet-overlay-pane path.leaflet-interactive:hover {
  filter: brightness(1.2);
}
`;

/**
 * Ray-casting point-in-polygon (algorithme classique)
 * Détermine si un point [lat, lng] est à l'intérieur d'un polygone
 * Convention Leaflet: coords = [[lat, lng], ...], yi=lat, xi=lng
 * Algorithme PIP standard: y=lat, x=lng
 */
function pointInPolygon(lat, lng, polygon) {
  let inside = false;
  const coords = Array.isArray(polygon[0]?.[0]) ? polygon[0] : polygon;
  for (let i = 0, j = coords.length - 1; i < coords.length; j = i++) {
    const [yi, xi] = coords[i]; // yi=lat, xi=lng
    const [yj, xj] = coords[j]; // yj=lat, xj=lng
    if (((yi > lat) !== (yj > lat)) && (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  return inside;
}

const BionicAntiDoublesGuard = ({ zones = [], onZoneClick }) => {
  const zonesRef = useRef(zones);
  zonesRef.current = zones;

  // Injection CSS au montage, suppression au démontage
  useEffect(() => {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = SUPPRESSION_CSS;
    document.head.appendChild(style);

    return () => {
      const existing = document.getElementById(STYLE_ID);
      if (existing) existing.remove();
    };
  }, []);

  // Détection de clic sur zone via ray-casting
  const handleMapClick = useCallback((e) => {
    if (!onZoneClick || !zonesRef.current.length) return;

    const { lat, lng } = e.latlng;

    // Parcourir les zones de la plus haute priorité (score) à la plus basse
    const sortedZones = [...zonesRef.current].sort((a, b) => b.score - a.score);

    for (const zone of sortedZones) {
      if (!zone.positions || !zone.positions.length) continue;
      if (pointInPolygon(lat, lng, zone.positions)) {
        onZoneClick(zone);
        return;
      }
    }

    // Clic hors zone : fermer le panneau
    onZoneClick(null);
  }, [onZoneClick]);

  useMapEvents({
    click: handleMapClick,
  });

  return null;
};

export default BionicAntiDoublesGuard;
