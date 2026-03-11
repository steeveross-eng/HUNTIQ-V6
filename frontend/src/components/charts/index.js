/**
 * Charts Module - PHASE F BIONIC ULTIMATE
 * 
 * Bibliothèque de graphiques légère remplaçant Recharts
 * ~15KB vs ~450KB
 * 
 * @module charts
 * @version 1.0.0
 */

export {
  LightPieChart,
  LightLineChart,
  LightBarChart,
  LightRadarChart,
  LightAreaChart,
  ResponsiveChartContainer
} from './LightCharts';

// Alias for compatibility with existing code
export { 
  LightPieChart as PieChart,
  LightLineChart as LineChart,
  LightBarChart as BarChart,
  LightRadarChart as RadarChart,
  LightAreaChart as AreaChart,
  ResponsiveChartContainer as ResponsiveContainer
} from './LightCharts';
