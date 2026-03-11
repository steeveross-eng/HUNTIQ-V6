/**
 * Lightweight Charts Library - PHASE F BIONIC ULTIMATE
 * 
 * Remplace Recharts (~450KB) par des composants SVG natifs (~15KB)
 * Conformité BIONIC V5 Design System
 * 
 * @module charts
 * @version 1.0.0
 * @phase F
 */

import React, { useMemo, memo } from 'react';

// ============================================================================
// CONSTANTS & HELPERS
// ============================================================================

const BIONIC_COLORS = {
  gold: '#F5A623',
  green: '#22c55e',
  blue: '#3b82f6',
  red: '#ef4444',
  purple: '#8b5cf6',
  orange: '#f97316',
  gray: '#6b7280'
};

const DEFAULT_COLORS = [
  BIONIC_COLORS.gold,
  BIONIC_COLORS.green,
  BIONIC_COLORS.blue,
  BIONIC_COLORS.purple,
  BIONIC_COLORS.orange,
  BIONIC_COLORS.red
];

/**
 * Calculate path for smooth line
 */
const getLinePath = (points, width, height, padding = 20) => {
  if (!points || points.length < 2) return '';
  
  const maxY = Math.max(...points.map(p => p.value));
  const minY = Math.min(...points.map(p => p.value));
  const range = maxY - minY || 1;
  
  const scaleX = (width - padding * 2) / (points.length - 1);
  const scaleY = (height - padding * 2) / range;
  
  return points.map((point, i) => {
    const x = padding + i * scaleX;
    const y = height - padding - (point.value - minY) * scaleY;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');
};

/**
 * Calculate area path (line + fill)
 */
const getAreaPath = (points, width, height, padding = 20) => {
  const linePath = getLinePath(points, width, height, padding);
  if (!linePath) return '';
  
  const lastX = padding + (points.length - 1) * ((width - padding * 2) / (points.length - 1));
  return `${linePath} L ${lastX} ${height - padding} L ${padding} ${height - padding} Z`;
};

// ============================================================================
// PIE CHART
// ============================================================================

/**
 * Lightweight Pie Chart component
 * Replaces recharts PieChart
 */
export const LightPieChart = memo(({ 
  data, 
  size = 200, 
  innerRadius = 0,
  colors = DEFAULT_COLORS,
  showLabels = true,
  showTooltip = true
}) => {
  const [hoveredIndex, setHoveredIndex] = React.useState(null);
  
  const { paths, total } = useMemo(() => {
    const total = data.reduce((sum, item) => sum + (item.value || 0), 0);
    if (total === 0) return { paths: [], total: 0 };
    
    const center = size / 2;
    const radius = (size - 20) / 2;
    const inner = innerRadius * radius;
    
    let currentAngle = -90; // Start from top
    
    const paths = data.map((item, index) => {
      const percentage = (item.value / total) * 100;
      const angle = (item.value / total) * 360;
      const startAngle = currentAngle;
      const endAngle = currentAngle + angle;
      currentAngle = endAngle;
      
      // Calculate arc path
      const startRad = (startAngle * Math.PI) / 180;
      const endRad = (endAngle * Math.PI) / 180;
      
      const x1 = center + radius * Math.cos(startRad);
      const y1 = center + radius * Math.sin(startRad);
      const x2 = center + radius * Math.cos(endRad);
      const y2 = center + radius * Math.sin(endRad);
      
      const ix1 = center + inner * Math.cos(startRad);
      const iy1 = center + inner * Math.sin(startRad);
      const ix2 = center + inner * Math.cos(endRad);
      const iy2 = center + inner * Math.sin(endRad);
      
      const largeArc = angle > 180 ? 1 : 0;
      
      let path;
      if (inner > 0) {
        // Donut
        path = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} L ${ix2} ${iy2} A ${inner} ${inner} 0 ${largeArc} 0 ${ix1} ${iy1} Z`;
      } else {
        // Pie
        path = `M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
      }
      
      // Label position
      const midAngle = (startAngle + endAngle) / 2;
      const midRad = (midAngle * Math.PI) / 180;
      const labelRadius = inner > 0 ? (radius + inner) / 2 : radius * 0.6;
      const labelX = center + labelRadius * Math.cos(midRad);
      const labelY = center + labelRadius * Math.sin(midRad);
      
      return {
        path,
        color: item.color || colors[index % colors.length],
        name: item.name,
        value: item.value,
        percentage,
        labelX,
        labelY
      };
    });
    
    return { paths, total };
  }, [data, size, innerRadius, colors]);
  
  if (paths.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-gray-500 text-sm">Aucune donnée</span>
      </div>
    );
  }
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="overflow-visible">
        {paths.map((slice, index) => (
          <g key={index}>
            <path
              d={slice.path}
              fill={slice.color}
              stroke="rgba(0,0,0,0.2)"
              strokeWidth="1"
              className="transition-opacity duration-200 cursor-pointer"
              opacity={hoveredIndex === null || hoveredIndex === index ? 1 : 0.5}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            />
            {showLabels && slice.percentage > 8 && (
              <text
                x={slice.labelX}
                y={slice.labelY}
                textAnchor="middle"
                dominantBaseline="middle"
                className="fill-white text-xs font-medium pointer-events-none"
                style={{ textShadow: '0 1px 2px rgba(0,0,0,0.5)' }}
              >
                {slice.percentage.toFixed(0)}%
              </text>
            )}
          </g>
        ))}
      </svg>
      
      {/* Tooltip */}
      {showTooltip && hoveredIndex !== null && (
        <div 
          className="absolute z-50 bg-black/90 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none"
          style={{ 
            left: '50%', 
            top: '50%', 
            transform: 'translate(-50%, -50%)'
          }}
        >
          <div className="font-medium">{paths[hoveredIndex].name}</div>
          <div className="text-gray-300">
            {paths[hoveredIndex].value} ({paths[hoveredIndex].percentage.toFixed(1)}%)
          </div>
        </div>
      )}
    </div>
  );
});

LightPieChart.displayName = 'LightPieChart';

// ============================================================================
// LINE CHART
// ============================================================================

/**
 * Lightweight Line Chart component
 * Replaces recharts LineChart
 */
export const LightLineChart = memo(({ 
  data,
  dataKey = 'value',
  nameKey = 'name',
  width = 300,
  height = 200,
  color = BIONIC_COLORS.gold,
  showGrid = true,
  showDots = true,
  showArea = false,
  padding = 30
}) => {
  const [hoveredIndex, setHoveredIndex] = React.useState(null);
  
  const { points, linePath, areaPath, maxY, minY } = useMemo(() => {
    if (!data || data.length === 0) return { points: [], linePath: '', areaPath: '' };
    
    const points = data.map((item, index) => ({
      name: item[nameKey],
      value: item[dataKey] || 0,
      index
    }));
    
    const maxY = Math.max(...points.map(p => p.value));
    const minY = Math.min(...points.map(p => p.value));
    
    return {
      points,
      linePath: getLinePath(points, width, height, padding),
      areaPath: showArea ? getAreaPath(points, width, height, padding) : '',
      maxY,
      minY
    };
  }, [data, dataKey, nameKey, width, height, padding, showArea]);
  
  if (points.length === 0) {
    return (
      <div className="flex items-center justify-center bg-black/20 rounded" style={{ width, height }}>
        <span className="text-gray-500 text-sm">Aucune donnée</span>
      </div>
    );
  }
  
  const scaleX = (width - padding * 2) / (points.length - 1);
  const range = maxY - minY || 1;
  const scaleY = (height - padding * 2) / range;
  
  return (
    <div className="relative" style={{ width, height }}>
      <svg width={width} height={height} className="overflow-visible">
        {/* Grid */}
        {showGrid && (
          <g className="stroke-white/10">
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
              <line
                key={i}
                x1={padding}
                y1={padding + (height - padding * 2) * ratio}
                x2={width - padding}
                y2={padding + (height - padding * 2) * ratio}
              />
            ))}
          </g>
        )}
        
        {/* Area fill */}
        {showArea && areaPath && (
          <path
            d={areaPath}
            fill={color}
            fillOpacity={0.2}
          />
        )}
        
        {/* Line */}
        <path
          d={linePath}
          fill="none"
          stroke={color}
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Dots */}
        {showDots && points.map((point, i) => {
          const x = padding + i * scaleX;
          const y = height - padding - (point.value - minY) * scaleY;
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={hoveredIndex === i ? 6 : 4}
              fill={color}
              stroke="white"
              strokeWidth={2}
              className="cursor-pointer transition-all duration-150"
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
            />
          );
        })}
        
        {/* X-axis labels */}
        {points.map((point, i) => {
          if (points.length > 7 && i % 2 !== 0) return null;
          const x = padding + i * scaleX;
          return (
            <text
              key={i}
              x={x}
              y={height - 5}
              textAnchor="middle"
              className="fill-gray-400 text-[10px]"
            >
              {typeof point.name === 'string' ? point.name.slice(0, 6) : point.name}
            </text>
          );
        })}
      </svg>
      
      {/* Tooltip */}
      {hoveredIndex !== null && (
        <div 
          className="absolute z-50 bg-black/90 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none"
          style={{ 
            left: padding + hoveredIndex * scaleX,
            top: height - padding - (points[hoveredIndex].value - minY) * scaleY - 40,
            transform: 'translateX(-50%)'
          }}
        >
          <div className="font-medium">{points[hoveredIndex].name}</div>
          <div style={{ color }}>{points[hoveredIndex].value}</div>
        </div>
      )}
    </div>
  );
});

LightLineChart.displayName = 'LightLineChart';

// ============================================================================
// BAR CHART
// ============================================================================

/**
 * Lightweight Bar Chart component
 * Replaces recharts BarChart
 */
export const LightBarChart = memo(({ 
  data,
  dataKey = 'value',
  nameKey = 'name',
  width = 300,
  height = 200,
  color = BIONIC_COLORS.gold,
  colors,
  showGrid = true,
  horizontal = false,
  padding = 40
}) => {
  const [hoveredIndex, setHoveredIndex] = React.useState(null);
  
  const { bars, maxValue } = useMemo(() => {
    if (!data || data.length === 0) return { bars: [], maxValue: 0 };
    
    const maxValue = Math.max(...data.map(item => item[dataKey] || 0));
    
    const bars = data.map((item, index) => ({
      name: item[nameKey],
      value: item[dataKey] || 0,
      color: item.color || (colors ? colors[index % colors.length] : color),
      percentage: maxValue > 0 ? (item[dataKey] / maxValue) * 100 : 0
    }));
    
    return { bars, maxValue };
  }, [data, dataKey, nameKey, color, colors]);
  
  if (bars.length === 0) {
    return (
      <div className="flex items-center justify-center bg-black/20 rounded" style={{ width, height }}>
        <span className="text-gray-500 text-sm">Aucune donnée</span>
      </div>
    );
  }
  
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;
  const barWidth = horizontal 
    ? chartHeight / bars.length - 4
    : chartWidth / bars.length - 4;
  
  return (
    <div className="relative" style={{ width, height }}>
      <svg width={width} height={height} className="overflow-visible">
        {/* Grid */}
        {showGrid && (
          <g className="stroke-white/10">
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
              horizontal ? (
                <line
                  key={i}
                  x1={padding + chartWidth * ratio}
                  y1={padding}
                  x2={padding + chartWidth * ratio}
                  y2={height - padding}
                />
              ) : (
                <line
                  key={i}
                  x1={padding}
                  y1={padding + chartHeight * (1 - ratio)}
                  x2={width - padding}
                  y2={padding + chartHeight * (1 - ratio)}
                />
              )
            ))}
          </g>
        )}
        
        {/* Bars */}
        {bars.map((bar, i) => {
          const barLength = (bar.percentage / 100) * (horizontal ? chartWidth : chartHeight);
          
          const x = horizontal 
            ? padding 
            : padding + i * (chartWidth / bars.length) + 2;
          const y = horizontal 
            ? padding + i * (chartHeight / bars.length) + 2
            : height - padding - barLength;
          const w = horizontal ? barLength : barWidth;
          const h = horizontal ? barWidth : barLength;
          
          return (
            <g key={i}>
              <rect
                x={x}
                y={y}
                width={Math.max(w, 2)}
                height={Math.max(h, 2)}
                fill={bar.color}
                rx={2}
                className="cursor-pointer transition-opacity duration-150"
                opacity={hoveredIndex === null || hoveredIndex === i ? 1 : 0.5}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
              {/* Label */}
              {!horizontal && (
                <text
                  x={x + barWidth / 2}
                  y={height - padding + 15}
                  textAnchor="middle"
                  className="fill-gray-400 text-[10px]"
                >
                  {typeof bar.name === 'string' ? bar.name.slice(0, 4) : bar.name}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      
      {/* Tooltip */}
      {hoveredIndex !== null && (
        <div 
          className="absolute z-50 bg-black/90 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none"
          style={{ 
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)'
          }}
        >
          <div className="font-medium">{bars[hoveredIndex].name}</div>
          <div style={{ color: bars[hoveredIndex].color }}>{bars[hoveredIndex].value}</div>
        </div>
      )}
    </div>
  );
});

LightBarChart.displayName = 'LightBarChart';

// ============================================================================
// RADAR CHART
// ============================================================================

/**
 * Lightweight Radar Chart component
 * Replaces recharts RadarChart
 */
export const LightRadarChart = memo(({ 
  data,
  size = 200,
  color = BIONIC_COLORS.gold,
  maxValue = 100,
  showLabels = true
}) => {
  const center = size / 2;
  const radius = (size - 40) / 2;
  
  const { points, polygon, gridPaths } = useMemo(() => {
    if (!data || data.length < 3) return { points: [], polygon: '', gridPaths: [] };
    
    const angleStep = (2 * Math.PI) / data.length;
    const startAngle = -Math.PI / 2; // Start from top
    
    const points = data.map((item, i) => {
      const angle = startAngle + i * angleStep;
      const value = Math.min(item.value || 0, maxValue);
      const r = (value / maxValue) * radius;
      return {
        x: center + r * Math.cos(angle),
        y: center + r * Math.sin(angle),
        labelX: center + (radius + 15) * Math.cos(angle),
        labelY: center + (radius + 15) * Math.sin(angle),
        name: item.name,
        value: item.value,
        angle
      };
    });
    
    const polygon = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
    
    // Grid circles
    const gridPaths = [0.25, 0.5, 0.75, 1].map(ratio => {
      const r = radius * ratio;
      return data.map((_, i) => {
        const angle = startAngle + i * angleStep;
        const x = center + r * Math.cos(angle);
        const y = center + r * Math.sin(angle);
        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
      }).join(' ') + ' Z';
    });
    
    return { points, polygon, gridPaths };
  }, [data, size, maxValue, center, radius]);
  
  if (points.length < 3) {
    return (
      <div className="flex items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-gray-500 text-sm">Minimum 3 points requis</span>
      </div>
    );
  }
  
  return (
    <svg width={size} height={size} className="overflow-visible">
      {/* Grid */}
      {gridPaths.map((path, i) => (
        <path
          key={i}
          d={path}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={1}
        />
      ))}
      
      {/* Axes */}
      {points.map((point, i) => (
        <line
          key={i}
          x1={center}
          y1={center}
          x2={center + radius * Math.cos(point.angle)}
          y2={center + radius * Math.sin(point.angle)}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={1}
        />
      ))}
      
      {/* Data polygon */}
      <path
        d={polygon}
        fill={color}
        fillOpacity={0.3}
        stroke={color}
        strokeWidth={2}
      />
      
      {/* Data points */}
      {points.map((point, i) => (
        <circle
          key={i}
          cx={point.x}
          cy={point.y}
          r={4}
          fill={color}
          stroke="white"
          strokeWidth={2}
        />
      ))}
      
      {/* Labels */}
      {showLabels && points.map((point, i) => (
        <text
          key={i}
          x={point.labelX}
          y={point.labelY}
          textAnchor="middle"
          dominantBaseline="middle"
          className="fill-gray-300 text-[10px]"
        >
          {typeof point.name === 'string' ? point.name.slice(0, 8) : point.name}
        </text>
      ))}
    </svg>
  );
});

LightRadarChart.displayName = 'LightRadarChart';

// ============================================================================
// AREA CHART
// ============================================================================

/**
 * Lightweight Area Chart component
 * Replaces recharts AreaChart
 */
export const LightAreaChart = memo((props) => {
  return <LightLineChart {...props} showArea={true} />;
});

LightAreaChart.displayName = 'LightAreaChart';

// ============================================================================
// RESPONSIVE CONTAINER
// ============================================================================

/**
 * Responsive Container wrapper
 * Replaces recharts ResponsiveContainer
 */
export const ResponsiveChartContainer = memo(({ 
  children, 
  width = '100%', 
  height = 200,
  aspect
}) => {
  const containerRef = React.useRef(null);
  const [dimensions, setDimensions] = React.useState({ width: 300, height });
  
  React.useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width: containerWidth } = containerRef.current.getBoundingClientRect();
        const calculatedHeight = aspect ? containerWidth / aspect : height;
        setDimensions({
          width: containerWidth,
          height: typeof height === 'number' ? height : calculatedHeight
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [height, aspect]);
  
  return (
    <div 
      ref={containerRef} 
      style={{ width, height: typeof height === 'number' ? height : 'auto' }}
    >
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            width: dimensions.width,
            height: dimensions.height
          });
        }
        return child;
      })}
    </div>
  );
});

ResponsiveChartContainer.displayName = 'ResponsiveChartContainer';

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  LightPieChart,
  LightLineChart,
  LightBarChart,
  LightRadarChart,
  LightAreaChart,
  ResponsiveChartContainer
};
