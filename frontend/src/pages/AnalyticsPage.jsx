/**
 * AnalyticsPage - Phase P3 Analytics Dashboard Page
 * OPTIMISATION ERGONOMIQUE - Full Viewport Premium
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AnalyticsDashboard } from '../modules/analytics';
import { BarChart3, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

const AnalyticsPage = () => {
  const navigate = useNavigate();
  
  return (
    <div 
      className="fixed inset-0 bg-slate-900 flex flex-col overflow-hidden"
      style={{ paddingTop: '64px' }}
      data-testid="analytics-page"
    >
      {/* Header compact */}
      <div className="flex-shrink-0 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700/50 px-4 py-2">
        <div className="flex items-center gap-3">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => navigate('/')} 
            className="text-gray-400 hover:text-white h-8 px-2"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="h-5 w-px bg-slate-700" />
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[#f5a623]" />
            <div>
              <h1 className="text-sm font-bold text-white leading-tight">Analytics BIONIC™</h1>
              <p className="text-[10px] text-slate-400 leading-tight">
                Tableau de bord • Phase P3
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content area - full remaining height with scroll */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-4">
          <AnalyticsDashboard />
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
