/**
 * ActivityChart - Behavioral activity patterns display
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { BehavioralService } from '../BehavioralService';
import { BarChart3, Sunrise, Sunset, Leaf, BedDouble, Route, Loader2 } from 'lucide-react';

export const ActivityChart = ({ 
  species = 'deer',
  date = null
}) => {
  const [patterns, setPatterns] = useState([]);
  const [zones, setZones] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const patternsResult = await BehavioralService.getActivityPatterns(species, date);
      if (patternsResult.success && patternsResult.patterns?.length > 0) {
        setPatterns(patternsResult.patterns);
      } else {
        setPatterns(BehavioralService.getPlaceholderActivityPatterns());
      }
      setZones(BehavioralService.getPlaceholderZones());
    } catch (error) {
      console.error('Activity patterns error:', error);
      setPatterns(BehavioralService.getPlaceholderActivityPatterns());
      setZones(BehavioralService.getPlaceholderZones());
    } finally {
      setLoading(false);
    }
  }, [species, date]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getActivityColor = (value) => {
    if (value >= 80) return '#10b981';
    if (value >= 60) return '#22c55e';
    if (value >= 40) return '#f59e0b';
    if (value >= 20) return '#f97316';
    return '#64748b';
  };

  const maxActivity = Math.max(...patterns.map(p => p.activity), 1);

  return (
    <Card className="bg-gradient-to-br from-cyan-900/20 to-slate-900 border-cyan-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-cyan-400" />
            Patterns d'Activité
          </span>
          <Badge className="bg-cyan-900/50 text-cyan-400">
            Behavioral
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-6">
            <Loader2 className="h-8 w-8 animate-spin text-cyan-400 mx-auto" />
            <p className="text-slate-400 text-sm mt-2">Analyse comportementale...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Activity Chart */}
            <div className="bg-slate-800/50 rounded-lg p-3">
              <p className="text-slate-400 text-xs mb-3">Activité par heure</p>
              <div className="flex items-end gap-1 h-24">
                {patterns.map((p, index) => (
                  <div 
                    key={index}
                    className="flex-1 flex flex-col items-center"
                  >
                    <div 
                      className="w-full rounded-t transition-all"
                      style={{ 
                        height: `${(p.activity / maxActivity) * 100}%`,
                        backgroundColor: getActivityColor(p.activity),
                        minHeight: '4px'
                      }}
                    />
                  </div>
                ))}
              </div>
              <div className="flex justify-between mt-1 text-xs text-slate-500">
                <span>05h</span>
                <span>12h</span>
                <span>20h</span>
              </div>
            </div>

            {/* Peak Hours */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-emerald-900/30 rounded-lg p-3 text-center border border-emerald-700/50">
                <Sunrise className="h-6 w-6 text-emerald-400 mx-auto mb-1" />
                <div className="text-white font-bold">06:00 - 08:00</div>
                <div className="text-emerald-400 text-xs">Pic matinal</div>
              </div>
              <div className="bg-amber-900/30 rounded-lg p-3 text-center border border-amber-700/50">
                <Sunset className="h-6 w-6 text-amber-400 mx-auto mb-1" />
                <div className="text-white font-bold">17:00 - 19:00</div>
                <div className="text-amber-400 text-xs">Pic crépuscule</div>
              </div>
            </div>

            {/* Zones */}
            {zones && (
              <div className="space-y-2">
                <p className="text-slate-400 text-xs">Zones comportementales</p>
                
                {/* Feeding */}
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Leaf className="h-4 w-4 text-emerald-400" />
                    <span className="text-slate-300">Alimentation</span>
                    <Badge className="ml-auto bg-emerald-900/50 text-emerald-400 text-xs">
                      {zones.feeding[0]?.score || 0}%
                    </Badge>
                  </div>
                </div>

                {/* Bedding */}
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <div className="flex items-center gap-2 text-sm">
                    <BedDouble className="h-4 w-4 text-blue-400" />
                    <span className="text-slate-300">Repos</span>
                    <Badge className="ml-auto bg-blue-900/50 text-blue-400 text-xs">
                      {zones.bedding[0]?.score || 0}%
                    </Badge>
                  </div>
                </div>

                {/* Corridors */}
                <div className="bg-slate-800/50 rounded-lg p-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Route className="h-4 w-4 text-purple-400" />
                    <span className="text-slate-300">Corridors</span>
                    <Badge className="ml-auto bg-purple-900/50 text-purple-400 text-xs">
                      {zones.corridors?.length || 0} identifiés
                    </Badge>
                  </div>
                </div>
              </div>
            )}

            <Button 
              className="w-full bg-cyan-600 hover:bg-cyan-700 text-white"
              onClick={loadData}
            >
              Actualiser l'analyse
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ActivityChart;
