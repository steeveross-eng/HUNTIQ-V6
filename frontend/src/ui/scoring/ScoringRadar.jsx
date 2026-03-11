/**
 * ScoringRadar - V5-ULTIME
 * ========================
 * PHASE F: Migration vers LightCharts
 */

import React from 'react';
import { LightRadarChart } from '@/components/charts/LightCharts';

export const ScoringRadar = ({ data, color = '#F5A623', size = 'md' }) => {
  const sizes = {
    sm: 120,
    md: 200,
    lg: 300,
  };

  return (
    <div style={{ width: sizes[size], height: sizes[size] }}>
      <LightRadarChart 
        data={data} 
        size={sizes[size]} 
        color={color}
        maxValue={100}
        showLabels={size !== 'sm'}
      />
    </div>
  );
};

export default ScoringRadar;
