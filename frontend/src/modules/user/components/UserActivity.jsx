/**
 * UserActivity - User activity feed component
 * Phase 9 - Business Modules
 */
import React from 'react';
import { KeyRound, LogOut, ShoppingCart, Microscope, Scale, Heart, Star, Map, Pencil, Settings, ClipboardList } from 'lucide-react';

const ACTIVITY_ICONS = {
  login: KeyRound,
  logout: LogOut,
  purchase: ShoppingCart,
  analyze: Microscope,
  compare: Scale,
  favorite: Heart,
  review: Star,
  territory: Map,
  profile_update: Pencil,
  settings: Settings
};

const ACTIVITY_COLORS = {
  login: '#10b981',
  logout: '#64748b',
  purchase: '#f59e0b',
  analyze: '#3b82f6',
  compare: '#8b5cf6',
  favorite: '#ef4444',
  review: '#fbbf24',
  territory: '#22c55e'
};

export const UserActivity = ({ activities = [], limit = 10 }) => {
  const displayActivities = activities.slice(0, limit);

  const getActivityIcon = (type) => {
    return ACTIVITY_ICONS[type] || ClipboardList;
  };

  const getActivityColor = (type) => {
    return ACTIVITY_COLORS[type] || '#64748b';
  };

  if (!displayActivities.length) {
    return (
      <div className="bg-slate-800/50 rounded-lg p-4 text-center">
        <ClipboardList className="h-8 w-8 text-slate-500 mx-auto" />
        <p className="text-slate-400 text-sm mt-2">Aucune activité récente</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700">
      <div className="p-3 border-b border-slate-700">
        <h3 className="text-white font-medium flex items-center gap-2">
          <ClipboardList className="h-5 w-5 text-[#f5a623]" />
          Activité Récente
        </h3>
      </div>
      
      <div className="divide-y divide-slate-700">
        {displayActivities.map((activity, index) => {
          const IconComponent = getActivityIcon(activity.type);
          return (
            <div key={activity.id || index} className="p-3 hover:bg-slate-700/30 transition-colors">
              <div className="flex items-start gap-3">
                <IconComponent 
                  className="h-5 w-5 flex-shrink-0"
                  style={{ color: getActivityColor(activity.type) }}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">
                    {activity.description || activity.type}
                  </p>
                  <p className="text-slate-400 text-xs">
                    {activity.timestamp 
                      ? new Date(activity.timestamp).toLocaleString('fr-CA')
                      : 'Date inconnue'
                    }
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {activities.length > limit && (
        <div className="p-3 border-t border-slate-700 text-center">
          <button className="text-sm text-blue-400 hover:text-blue-300">
            Voir plus ({activities.length - limit} autres)
          </button>
        </div>
      )}
    </div>
  );
};

export default UserActivity;
