/**
 * TerritoryList - Territory listing component
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { TerritoryCard } from './TerritoryCard';
import { TerritoryService } from '../TerritoryService';
import { Map } from 'lucide-react';

export const TerritoryList = ({ 
  type = null,
  onSelect,
  onViewDetails,
  showFilters = true
}) => {
  const [territories, setTerritories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState(type);

  const loadTerritories = useCallback(async () => {
    setLoading(true);
    try {
      const result = await TerritoryService.getTerritories(filter);
      if (result.territories?.length > 0) {
        setTerritories(result.territories);
      } else {
        // Use placeholder
        setTerritories(TerritoryService.getPlaceholderTerritories());
      }
    } catch (error) {
      console.error('Load territories error:', error);
      setTerritories(TerritoryService.getPlaceholderTerritories());
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadTerritories();
  }, [loadTerritories]);

  const filteredTerritories = filter 
    ? territories.filter(t => t.type === filter)
    : territories;

  const types = ['zec', 'pourvoirie', 'public', 'reserve', 'private'];

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Map className="h-6 w-6 text-[#f5a623]" />
            Territoires de Chasse
          </span>
          <Badge className="bg-slate-700">{filteredTerritories.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        {showFilters && (
          <div className="flex flex-wrap gap-2 mb-4">
            <button
              onClick={() => setFilter(null)}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                !filter ? 'bg-[#f5a623] text-black' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Tous
            </button>
            {types.map(t => {
              const info = TerritoryService.getTerritoryTypeInfo(t);
              return (
                <button
                  key={t}
                  onClick={() => setFilter(t)}
                  className={`px-3 py-1 rounded-lg text-sm transition-all flex items-center gap-1 ${
                    filter === t ? 'bg-[#f5a623] text-black' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  <span>{info.icon}</span>
                  {info.label}
                </button>
              );
            })}
          </div>
        )}

        {/* List */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse bg-slate-700 rounded-lg h-32" />
            ))}
          </div>
        ) : filteredTerritories.length > 0 ? (
          <div className="space-y-3">
            {filteredTerritories.map(territory => (
              <TerritoryCard
                key={territory.id}
                territory={territory}
                onSelect={onSelect}
                onViewDetails={onViewDetails}
                compact
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Map className="h-10 w-10 text-[#f5a623] mx-auto" />
            <p className="text-slate-400 mt-2">Aucun territoire trouvé</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TerritoryList;
