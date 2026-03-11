/**
 * StrategyPanel - Main strategy recommendation panel
 * BIONIC Design System compliant - No emojis
 */
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Target, Loader2 } from 'lucide-react';
import { StrategyService } from '../StrategyService';
import { StrategyCard } from './StrategyCard';

export const StrategyPanel = ({ 
  species = 'deer',
  season = 'rut',
  weather = {},
  onStrategySelect
}) => {
  const [strategies, setStrategies] = useState([]);
  const [recommended, setRecommended] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStrategies();
  }, [species, season]);

  const loadStrategies = async () => {
    setLoading(true);
    try {
      const data = await StrategyService.getStrategies({ species, season });
      setStrategies(data.strategies || []);
    } catch (err) {
      console.error('Failed to load strategies:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendation = async () => {
    setLoading(true);
    try {
      const data = await StrategyService.getRecommendedStrategy({
        species,
        season,
        weather
      });
      setRecommended(data);
    } catch (err) {
      console.error('Failed to get recommendation:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Target className="w-6 h-6 text-[var(--bionic-gold-primary)]" />
            Stratégies de Chasse
          </span>
          <span className="text-xs text-slate-400 capitalize">{species} • {season}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Recommendation button */}
        <Button
          onClick={getRecommendation}
          disabled={loading}
          className="w-full mb-4 bg-emerald-600 hover:bg-emerald-500"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyse...</>
          ) : (
            <><Target className="w-4 h-4 mr-2" /> Obtenir la recommandation IA</>
          )}
        </Button>

        {/* Recommended strategy */}
        {recommended && (
          <div className="mb-4 p-3 bg-emerald-900/30 rounded-lg border border-emerald-700">
            <h4 className="text-emerald-400 font-medium text-sm mb-2 flex items-center gap-2">
              <Target className="w-4 h-4" />
              Stratégie Recommandée
            </h4>
            <StrategyCard 
              strategy={recommended.strategy || recommended}
              recommended
              onSelect={() => onStrategySelect?.(recommended)}
            />
          </div>
        )}

        {/* Strategy list */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse h-20 bg-slate-700 rounded-lg" />
            ))}
          </div>
        ) : strategies.length > 0 ? (
          <div className="space-y-3">
            {strategies.map((strategy, index) => (
              <StrategyCard
                key={strategy.id || index}
                strategy={strategy}
                onSelect={() => onStrategySelect?.(strategy)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center text-slate-400 py-4">
            Aucune stratégie disponible pour ces critères
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StrategyPanel;
