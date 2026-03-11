/**
 * SessionControls - Bottom control bar for session management
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Button } from '../../../components/ui/button';
import { Pause, Play, Square, Flag } from 'lucide-react';

export const SessionControls = ({ 
  sessionState, 
  onPauseResume, 
  onEnd, 
  onClose 
}) => {
  return (
    <div className="bg-slate-800/95 rounded-2xl p-4 border border-slate-700 shadow-xl">
      <div className="flex items-center justify-between gap-4">
        {/* Close button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="text-slate-400 hover:text-white"
        >
          ← Retour
        </Button>
        
        {/* Main controls */}
        <div className="flex items-center gap-2">
          {/* Pause/Resume */}
          <Button
            variant={sessionState === 'active' ? 'outline' : 'default'}
            size="lg"
            onClick={onPauseResume}
            disabled={sessionState === 'ended'}
            className={`
              min-w-24
              ${sessionState === 'paused' 
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white' 
                : 'border-slate-600 text-slate-300 hover:bg-slate-700'
              }
            `}
          >
            {sessionState === 'active' ? (
              <><Pause className="w-4 h-4 mr-1" /> Pause</>
            ) : sessionState === 'paused' ? (
              <><Play className="w-4 h-4 mr-1" /> Reprendre</>
            ) : (
              <><Square className="w-4 h-4 mr-1" /> Terminé</>
            )}
          </Button>
          
          {/* End session */}
          <Button
            variant="destructive"
            size="lg"
            onClick={onEnd}
            disabled={sessionState === 'ended'}
            className="bg-red-600 hover:bg-red-500 min-w-24"
          >
            <Flag className="w-4 h-4 mr-1" /> Fin
          </Button>
        </div>
        
        {/* Status indicator */}
        <div className="flex items-center gap-2">
          <div className={`
            w-3 h-3 rounded-full
            ${sessionState === 'active' 
              ? 'bg-emerald-500 animate-pulse' 
              : sessionState === 'paused'
                ? 'bg-amber-500'
                : 'bg-slate-500'
            }
          `} />
          <span className="text-sm text-slate-400 capitalize">
            {sessionState === 'active' ? 'Actif' 
              : sessionState === 'paused' ? 'En pause'
              : sessionState === 'ended' ? 'Terminé'
              : 'Initialisation...'
            }
          </span>
        </div>
      </div>
    </div>
  );
};

export default SessionControls;
