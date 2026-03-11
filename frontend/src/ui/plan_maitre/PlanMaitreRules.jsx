/**
 * PlanMaitreRules - V5-ULTIME Plan Maître
 * =======================================
 * 
 * Affichage et gestion des règles de chasse.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { 
  Book, Clock, Cloud, MapPin, Target, Lightbulb,
  ChevronDown, ChevronUp, Plus, Settings
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const RuleTypeIcons = {
  timing: Clock,
  weather: Cloud,
  territory: MapPin,
  scoring: Target,
  strategy: Lightbulb,
  legal: Book
};

const RulePriorityColors = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-gray-500'
};

const RuleCard = ({ rule, onToggle, expanded, onExpand }) => {
  const Icon = RuleTypeIcons[rule.type] || Book;
  
  return (
    <div className="bg-white/5 rounded-lg overflow-hidden">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5"
        onClick={() => onExpand?.(rule.name)}
      >
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${rule.enabled ? 'bg-[#F5A623]/20' : 'bg-white/10'}`}>
            <Icon className={`h-5 w-5 ${rule.enabled ? 'text-[#F5A623]' : 'text-gray-500'}`} />
          </div>
          <div>
            <h4 className={`font-medium ${rule.enabled ? 'text-white' : 'text-gray-500'}`}>
              {rule.name.replace(/_/g, ' ')}
            </h4>
            <p className="text-gray-500 text-xs capitalize">{rule.type}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={`${RulePriorityColors[rule.priority]} text-white text-xs`}>
            {rule.priority}
          </Badge>
          <Switch 
            checked={rule.enabled} 
            onCheckedChange={() => onToggle?.(rule.name, !rule.enabled)}
            onClick={(e) => e.stopPropagation()}
          />
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </div>
      
      {expanded && (
        <div className="px-4 pb-4 border-t border-white/10 pt-3">
          <p className="text-gray-400 text-sm mb-3">{rule.description}</p>
          
          {/* Conditions */}
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-2">Conditions:</p>
            <div className="flex flex-wrap gap-2">
              {rule.conditions?.map((cond, idx) => (
                <span key={idx} className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                  {cond.field} {cond.operator} {JSON.stringify(cond.value)}
                </span>
              ))}
            </div>
          </div>
          
          {/* Actions */}
          <div>
            <p className="text-xs text-gray-500 mb-2">Actions:</p>
            <div className="flex flex-wrap gap-2">
              {rule.actions?.map((action, idx) => (
                <span key={idx} className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">
                  {action.type}: {action.params?.modifier ? `x${action.params.modifier}` : action.params?.strategy || action.params?.message}
                </span>
              ))}
            </div>
          </div>
          
          {/* Species */}
          {rule.species && rule.species.length > 0 && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-xs text-gray-500">Espèces:</span>
              {rule.species.map((sp, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {sp}
                </Badge>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const PlanMaitreRules = ({ onRuleChange }) => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedRule, setExpandedRule] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchRules = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/api/v1/rules/list?enabled_only=false`);
        const data = await response.json();
        setRules(data.rules || []);
      } catch (error) {
        console.error('Failed to fetch rules:', error);
      }
      setLoading(false);
    };
    
    fetchRules();
  }, []);

  const handleToggle = async (ruleName, enabled) => {
    try {
      await fetch(`${API_BASE}/api/v1/rules/${ruleName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      });
      
      setRules(rules.map(r => 
        r.name === ruleName ? { ...r, enabled } : r
      ));
      
      onRuleChange?.({ ruleName, enabled });
    } catch (error) {
      console.error('Failed to toggle rule:', error);
    }
  };

  const ruleTypes = ['all', ...new Set(rules.map(r => r.type))];
  const filteredRules = filter === 'all' ? rules : rules.filter(r => r.type === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <Card className="bg-black/40 border-white/10">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-white flex items-center gap-2">
          <Book className="h-5 w-5 text-[#F5A623]" />
          Règles de Chasse
        </CardTitle>
        <Button size="sm" className="bg-[#F5A623] text-black hover:bg-[#F5A623]/90">
          <Plus className="h-4 w-4 mr-1" />
          Nouvelle règle
        </Button>
      </CardHeader>
      <CardContent>
        {/* Filter tabs */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
          {ruleTypes.map(type => (
            <Button
              key={type}
              size="sm"
              variant={filter === type ? 'default' : 'outline'}
              className={filter === type ? 'bg-[#F5A623] text-black' : 'border-white/20'}
              onClick={() => setFilter(type)}
            >
              {type === 'all' ? 'Toutes' : type}
            </Button>
          ))}
        </div>
        
        {/* Rules list */}
        <div className="space-y-3 max-h-[500px] overflow-y-auto">
          {filteredRules.map((rule, idx) => (
            <RuleCard
              key={idx}
              rule={rule}
              expanded={expandedRule === rule.name}
              onExpand={setExpandedRule}
              onToggle={handleToggle}
            />
          ))}
        </div>
        
        {filteredRules.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Aucune règle trouvée
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlanMaitreRules;
