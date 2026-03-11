/**
 * NutritionAnalysisModal.jsx — Nutrition Analysis Results
 * 
 * Full-screen modal showing species nutrition analysis:
 * food sources, nutritional gaps, product recommendations.
 * 
 * Phase 3 extraction from TerritoryMap.jsx
 * @module territory/NutritionAnalysisModal
 */

import React from 'react';
import { TreePine, Info, TrendingUp, ShoppingCart, ChevronRight, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

const NutritionAnalysisModal = ({ analysis, show, onClose, onAddToCart }) => {
  if (!show || !analysis) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-[2000] flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
          <div>
            <h2 className="text-white text-lg font-bold flex items-center gap-2">
              <TreePine className="h-5 w-5 text-[#f5a623]" />
              Analyse Alimentation
            </h2>
            <p className="text-gray-400 text-sm">
              {analysis.species?.name} - {analysis.environment?.season}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Summary */}
          <div className="bg-background rounded-lg p-3 border border-border">
            <p className="text-gray-300 text-sm">{analysis.summary}</p>
          </div>

          {/* Environment Info */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-background rounded-lg p-3 border border-border">
              <p className="text-gray-400 text-xs mb-1">Type de foret</p>
              <p className="text-white font-medium">{analysis.environment?.forest_type}</p>
              <p className="text-green-400 text-xs">Qualite: {analysis.environment?.food_quality}</p>
            </div>
            <div className="bg-background rounded-lg p-3 border border-border">
              <p className="text-gray-400 text-xs mb-1">Sources alimentaires</p>
              <div className="text-white text-sm">
                {analysis.food_sources_available?.slice(0, 3).map((source, i) => (
                  <span key={i} className="inline-block mr-1">- {source}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Nutritional Gaps */}
          <div>
            <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
              <Info className="h-4 w-4 text-yellow-500" />
              Carences identifiees
            </h3>
            <div className="space-y-2">
              {analysis.nutritional_gaps?.map((gap, idx) => (
                <div key={idx} className="bg-background rounded-lg p-2 border border-border flex items-center justify-between">
                  <div>
                    <span className="text-white font-medium capitalize">{gap.nutrient}</span>
                    <p className="text-gray-400 text-xs">{gap.reason}</p>
                  </div>
                  <Badge className={`${gap.severity === 'high' ? 'bg-red-500' : gap.severity === 'moderate' ? 'bg-yellow-500' : 'bg-green-500'}`}>
                    {gap.severity}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Product Recommendations */}
          <div>
            <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-[#f5a623]" />
              Produits Recommandes
            </h3>
            <div className="space-y-3">
              {analysis.recommended_products?.slice(0, 5).map((product, idx) => (
                <div
                  key={product.id}
                  className={`rounded-xl p-4 border ${!product.is_competitor ? 'bg-[#f5a623]/10 border-[#f5a623]/50' : 'bg-background border-border'}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={`${idx === 0 ? 'bg-[#f5a623] text-black' : 'bg-gray-600'}`}>#{idx + 1}</Badge>
                      <h4 className="text-white font-semibold">{product.name}</h4>
                      {!product.is_competitor && (
                        <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC</Badge>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-[#f5a623] font-bold">{product.relevance_score}</div>
                      <div className="text-gray-500 text-xs">score</div>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">{product.description}</p>
                  {product.matching_nutrients?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {product.matching_nutrients.map((nutrient, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-green-500 text-green-400">
                          {nutrient}
                        </Badge>
                      ))}
                    </div>
                  )}
                  <div className="bg-black/20 rounded-lg p-2 mt-2">
                    <p className="text-xs text-gray-400">
                      <span className="text-[#f5a623]">Pourquoi ce produit:</span> {product.recommendation_reason}
                    </p>
                  </div>
                  {product.benefits && (
                    <div className="mt-2 grid grid-cols-2 gap-1">
                      {product.benefits.slice(0, 4).map((benefit, i) => (
                        <div key={i} className="text-xs text-gray-400 flex items-center gap-1">
                          <ChevronRight className="h-3 w-3 text-[#f5a623]" />
                          {benefit}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-xs">Prix:</span>
                      <span className="text-white">{product.price_range}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-gray-400 text-xs">Efficacite:</span>
                      <span className="text-[#f5a623] font-medium">{product.effectiveness_rating}/10</span>
                    </div>
                  </div>
                  <Button
                    className="w-full mt-3 btn-golden text-black"
                    size="sm"
                    onClick={() => onAddToCart({
                      id: product.id,
                      name: product.name,
                      price: product.price_range === '$' ? 19.99 : product.price_range === '$$' ? 34.99 : product.price_range === '$$$' ? 49.99 : 69.99,
                      category: product.category,
                      is_bionic: !product.is_competitor
                    })}
                    data-testid={`add-to-cart-${product.id}`}
                  >
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Ajouter au panier
                  </Button>
                </div>
              ))}
            </div>
          </div>

          {/* Seasonal Notes */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Info className="h-4 w-4 text-blue-400" />
              <span className="text-blue-400 font-medium text-sm">Note saisonniere</span>
            </div>
            <p className="text-gray-300 text-sm">{analysis.seasonal_analysis?.notes}</p>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-card border-t border-border p-4">
          <Button className="w-full btn-golden text-black" onClick={onClose}>
            Fermer l'analyse
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NutritionAnalysisModal;
