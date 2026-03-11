/**
 * AIInsights - AI-generated insights display
 * BIONIC Design System compliant
 */
import React from 'react';
import { AlertTriangle, CheckCircle, Info, Lightbulb, TrendingUp, AlertCircle, Brain } from 'lucide-react';

// Insight icons - BIONIC Design System (Lucide components)
const InsightIcon = ({ type, className = "h-5 w-5" }) => {
  const iconMap = {
    warning: { Icon: AlertTriangle, color: '#f59e0b' },
    success: { Icon: CheckCircle, color: '#10b981' },
    info: { Icon: Info, color: '#3b82f6' },
    tip: { Icon: Lightbulb, color: '#8b5cf6' },
    trend: { Icon: TrendingUp, color: '#06b6d4' },
    alert: { Icon: AlertCircle, color: '#ef4444' }
  };
  
  const { Icon, color } = iconMap[type] || { Icon: Lightbulb, color: '#8b5cf6' };
  return <Icon className={className} style={{ color }} />;
};

export const AIInsights = ({ insights = [], title = 'Insights IA' }) => {
  if (!insights.length) {
    return (
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 text-center">
        <Brain className="h-8 w-8 text-[#f5a623] mx-auto" />
        <p className="text-slate-400 text-sm mt-2">Aucun insight disponible</p>
      </div>
    );
  }

  const getInsightColor = (type) => {
    const colors = {
      warning: 'border-amber-700 bg-amber-900/20',
      success: 'border-emerald-700 bg-emerald-900/20',
      info: 'border-blue-700 bg-blue-900/20',
      tip: 'border-purple-700 bg-purple-900/20',
      trend: 'border-cyan-700 bg-cyan-900/20',
      alert: 'border-red-700 bg-red-900/20'
    };
    return colors[type] || 'border-slate-700 bg-slate-800/50';
  };

  return (
    <div className="space-y-3">
      <h3 className="text-white font-medium flex items-center gap-2">
        <Brain className="h-5 w-5 text-[#f5a623]" />
        {title}
      </h3>
      
      {insights.map((insight, index) => (
        <div
          key={index}
          className={`rounded-lg border p-3 ${getInsightColor(insight.type)}`}
        >
          <div className="flex items-start gap-3">
            <InsightIcon type={insight.type} className="h-5 w-5 flex-shrink-0" />
            <div className="flex-1">
              {insight.title && (
                <h4 className="text-white font-medium text-sm mb-1">
                  {insight.title}
                </h4>
              )}
              <p className="text-slate-300 text-sm">
                {insight.message || insight.content}
              </p>
              {insight.action && (
                <button className="mt-2 text-xs text-purple-400 hover:text-purple-300">
                  {insight.action} →
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AIInsights;
