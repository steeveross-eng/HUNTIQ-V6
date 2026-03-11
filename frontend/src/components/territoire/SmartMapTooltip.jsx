/**
 * SmartMapTooltip — Tooltip avec collision avoidance pour Leaflet
 * 
 * Remplace le Leaflet <Tooltip sticky> par un tooltip React qui 
 * se repositionne automatiquement pour rester dans la zone visible.
 * 
 * COMPORTEMENT:
 * - Par défaut: tooltip AU-DESSUS du curseur
 * - Si collision avec le header: tooltip EN-DESSOUS du curseur
 * - max-height: 80vh avec scroll interne
 * - z-index: 1000 (au-dessus du header, en-dessous des overlays critiques)
 * 
 * AUCUNE MODIFICATION du layout global.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useMap } from 'react-leaflet';
import ReactDOM from 'react-dom';

const HEADER_SAFE_ZONE = 178; // nav(64) + header(60) + tabs(44) + marge(10)
const TOOLTIP_OFFSET = 15;

const SmartMapTooltip = ({ children, show, containerPoint }) => {
  const map = useMap();
  const tooltipRef = useRef(null);
  const [adjustedPos, setAdjustedPos] = useState({ x: 0, y: 0, direction: 'top' });

  useEffect(() => {
    if (!show || !containerPoint || !map) return;

    const mapContainer = map.getContainer();
    const mapRect = mapContainer.getBoundingClientRect();
    const tooltipEl = tooltipRef.current;
    
    let tooltipHeight = 320; // estimation par défaut
    if (tooltipEl) {
      tooltipHeight = tooltipEl.offsetHeight;
    }

    // Position absolue dans le viewport
    const viewportX = mapRect.left + containerPoint.x;
    const viewportY = mapRect.top + containerPoint.y;

    let finalX = viewportX;
    let finalY;
    let direction = 'top';

    // Test collision: si le tooltip au-dessus dépasserait le header
    if (viewportY - tooltipHeight - TOOLTIP_OFFSET < HEADER_SAFE_ZONE) {
      // Positionner EN-DESSOUS du curseur
      finalY = viewportY + TOOLTIP_OFFSET;
      direction = 'bottom';
    } else {
      // Positionner AU-DESSUS du curseur (comportement par défaut)
      finalY = viewportY - tooltipHeight - TOOLTIP_OFFSET;
      direction = 'top';
    }

    // Clamper pour ne jamais dépasser le bas du viewport
    const maxY = window.innerHeight - tooltipHeight - 10;
    finalY = Math.min(finalY, maxY);
    
    // Clamper pour ne jamais dépasser les bords horizontaux
    const tooltipWidth = tooltipEl ? tooltipEl.offsetWidth : 260;
    finalX = Math.max(10, Math.min(finalX - tooltipWidth / 2, window.innerWidth - tooltipWidth - 10));

    setAdjustedPos({ x: finalX, y: finalY, direction });
  }, [show, containerPoint, map]);

  if (!show) return null;

  // Render via portal au body level pour échapper au stacking context
  return ReactDOM.createPortal(
    <div
      ref={tooltipRef}
      className="bionic-smart-tooltip"
      style={{
        position: 'fixed',
        left: `${adjustedPos.x}px`,
        top: `${adjustedPos.y}px`,
        zIndex: 1000,
        pointerEvents: 'auto',
        maxHeight: '80vh',
        overflowY: 'auto',
        transition: 'left 0.05s ease-out, top 0.05s ease-out',
      }}
    >
      {children}
      <div 
        className="bionic-smart-tooltip-arrow"
        style={{
          position: 'absolute',
          left: '50%',
          transform: 'translateX(-50%)',
          ...(adjustedPos.direction === 'top' 
            ? { bottom: '-6px', borderLeft: '6px solid transparent', borderRight: '6px solid transparent', borderTop: '6px solid rgba(17,24,39,0.95)' }
            : { top: '-6px', borderLeft: '6px solid transparent', borderRight: '6px solid transparent', borderBottom: '6px solid rgba(17,24,39,0.95)' }
          ),
          width: 0,
          height: 0,
        }}
      />
    </div>,
    document.body
  );
};

export default SmartMapTooltip;
