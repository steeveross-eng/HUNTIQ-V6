/**
 * ScoreCompare - Compare two products' scores
 */
import React from 'react';
import { ScoreDisplay } from './ScoreDisplay';
import { Trophy } from 'lucide-react';

export const ScoreCompare = ({ 
  productA, 
  productB,
  title = 'Comparaison'
}) => {
  if (!productA || !productB) {
    return (
      <div className="text-center text-slate-400 py-8">
        Sélectionnez deux produits à comparer
      </div>
    );
  }

  const diff = productA.score - productB.score;

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <h3 className="text-white font-medium mb-4 text-center">{title}</h3>
      
      <div className="flex items-center justify-around">
        {/* Product A */}
        <div className="text-center">
          <ScoreDisplay score={productA.score} size="md" showLabel={false} />
          <p className="mt-2 text-sm text-white font-medium truncate max-w-24">
            {productA.name}
          </p>
        </div>
        
        {/* VS */}
        <div className="flex flex-col items-center px-4">
          <span className="text-slate-500 text-sm">VS</span>
          <div className={`text-lg font-bold mt-1 ${diff > 0 ? 'text-emerald-400' : diff < 0 ? 'text-red-400' : 'text-slate-400'}`}>
            {diff > 0 ? '+' : ''}{diff}
          </div>
        </div>
        
        {/* Product B */}
        <div className="text-center">
          <ScoreDisplay score={productB.score} size="md" showLabel={false} />
          <p className="mt-2 text-sm text-white font-medium truncate max-w-24">
            {productB.name}
          </p>
        </div>
      </div>
      
      {/* Winner badge */}
      {diff !== 0 && (
        <div className="mt-4 text-center">
          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium
            ${diff > 0 ? 'bg-emerald-900/50 text-emerald-400' : 'bg-blue-900/50 text-blue-400'}`}>
            <Trophy className="h-3 w-3" /> {diff > 0 ? productA.name : productB.name} gagne
          </span>
        </div>
      )}
    </div>
  );
};

export default ScoreCompare;
