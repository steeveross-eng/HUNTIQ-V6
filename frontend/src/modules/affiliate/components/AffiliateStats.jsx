/**
 * AffiliateStats - Affiliate statistics display
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Link2, DollarSign } from 'lucide-react';

export const AffiliateStats = ({ stats = {} }) => {
  const {
    total_clicks = 0,
    total_sales = 0,
    total_commission = 0,
    conversion_rate = 0,
    pending_commission = 0
  } = stats;

  return (
    <Card className="bg-gradient-to-br from-purple-900/30 to-slate-900 border-purple-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Link2 className="w-6 h-6 text-purple-400" />
          Statistiques Affiliation
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-blue-400">{total_clicks}</div>
            <div className="text-xs text-slate-400">Clics</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-emerald-400">{total_sales}</div>
            <div className="text-xs text-slate-400">Ventes</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-amber-400">{conversion_rate.toFixed(1)}%</div>
            <div className="text-xs text-slate-400">Conversion</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-[#f5a623]">{total_commission.toFixed(2)}$</div>
            <div className="text-xs text-slate-400">Commission</div>
          </div>
        </div>

        {pending_commission > 0 && (
          <div className="mt-4 p-3 bg-amber-900/30 rounded-lg border border-amber-700">
            <p className="text-sm text-amber-300 flex items-center gap-2">
              <DollarSign className="w-4 h-4" /> {pending_commission.toFixed(2)}$ en commission en attente
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AffiliateStats;
