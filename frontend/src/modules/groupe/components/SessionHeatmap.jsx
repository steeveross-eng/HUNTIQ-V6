/**
 * SessionHeatmap - Heatmap layer for group session GPS density
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 6
 * 
 * Displays GPS position density of group members during active session.
 * Read-only visualization layer.
 * 
 * Data source: ONLY GPS positions from group members (live)
 * Integration: Overlay on GROUPE map via HeatmapLayer
 */
import React, { useMemo } from 'react';
import { HeatmapLayer } from '../../../components/HeatmapLayer';

/**
 * SessionHeatmap Component
 * 
 * @param {Array} membersWithPositions - Array of members with valid GPS positions
 *   Each member object must have: { position: { lat: number, lng: number } }
 * @param {boolean} isActive - Whether the session is active (tracking enabled)
 */
export const SessionHeatmap = ({ 
  membersWithPositions = [], 
  isActive = false 
}) => {
  // Transform member positions to heatmap data format
  // Format: [lat, lng, intensity]
  // NOTE: useMemo must be called before any early returns (React hooks rules)
  const heatmapData = useMemo(() => {
    if (!membersWithPositions || membersWithPositions.length === 0) {
      return [];
    }
    return membersWithPositions
      .filter(member => member.position?.lat && member.position?.lng)
      .map(member => ({
        lat: member.position.lat,
        lng: member.position.lng,
        intensity: 0.7 // Fixed intensity for GPS density visualization
      }));
  }, [membersWithPositions]);

  // Only render when session is active and has data
  if (!isActive || heatmapData.length === 0) {
    return null;
  }

  // Heatmap configuration for GPS density visualization
  // BIONIC color scheme: blue (low) -> gold (medium) -> red (high density)
  const heatmapOptions = {
    radius: 25,
    blur: 15,
    maxZoom: 17,
    max: 1.0,
    gradient: {
      0.0: '#3b82f6',   // Blue - sparse
      0.4: '#22c55e',   // Green - moderate
      0.6: '#f5a623',   // Gold (BIONIC primary) - good density
      0.8: '#ef4444',   // Red - high density
      1.0: '#dc2626'    // Dark red - hotspot
    }
  };

  return (
    <HeatmapLayer 
      data={heatmapData} 
      options={heatmapOptions}
    />
  );
};

export default SessionHeatmap;
