/**
 * CartWidget - Shopping cart widget component
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { ShoppingCart, Trash2 } from 'lucide-react';

export const CartWidget = ({ 
  items = [], 
  onUpdateQuantity, 
  onRemoveItem, 
  onCheckout,
  onClear,
  compact = false
}) => {
  const total = items.reduce((sum, item) => {
    const price = item.product?.price || item.price || 0;
    return sum + (price * item.quantity);
  }, 0);

  const itemCount = items.reduce((count, item) => count + item.quantity, 0);

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-slate-800/80 rounded-lg px-4 py-2">
        <ShoppingCart className="w-5 h-5 text-slate-300" />
        <div>
          <span className="text-white font-medium">{itemCount} article{itemCount > 1 ? 's' : ''}</span>
          <span className="text-[#f5a623] font-bold ml-2">{total.toFixed(2)}$</span>
        </div>
      </div>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <ShoppingCart className="w-6 h-6 text-slate-300" />
            Panier
          </span>
          <Badge className="bg-[#f5a623] text-black">
            {itemCount}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="text-center py-8">
            <ShoppingCart className="w-12 h-12 text-slate-500 mx-auto" />
            <p className="text-slate-400 mt-2">Votre panier est vide</p>
          </div>
        ) : (
          <>
            {/* Items List */}
            <div className="space-y-3 max-h-64 overflow-y-auto mb-4">
              {items.map((item) => (
                <div key={item.id} className="flex items-center gap-3 bg-slate-700/50 rounded-lg p-2">
                  {item.product?.image_url && (
                    <img 
                      src={item.product.image_url} 
                      alt={item.product.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">
                      {item.product?.name || item.name}
                    </p>
                    <p className="text-[#f5a623] text-sm">
                      {(item.product?.price || item.price || 0).toFixed(2)}$
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    {onUpdateQuantity && (
                      <>
                        <button
                          onClick={() => onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                          className="w-6 h-6 bg-slate-600 rounded text-white text-sm hover:bg-slate-500"
                        >
                          -
                        </button>
                        <span className="text-white text-sm w-6 text-center">{item.quantity}</span>
                        <button
                          onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                          className="w-6 h-6 bg-slate-600 rounded text-white text-sm hover:bg-slate-500"
                        >
                          +
                        </button>
                      </>
                    )}
                    {onRemoveItem && (
                      <button
                        onClick={() => onRemoveItem(item.id)}
                        className="ml-2 text-red-400 hover:text-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Total */}
            <div className="flex justify-between items-center py-3 border-t border-slate-700">
              <span className="text-white font-medium">Total</span>
              <span className="text-[#f5a623] font-bold text-xl">
                {total.toFixed(2)}$
              </span>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              {onCheckout && (
                <Button 
                  className="w-full bg-[#f5a623] hover:bg-[#d4890e] text-black font-semibold"
                  onClick={onCheckout}
                >
                  Commander
                </Button>
              )}
              {onClear && items.length > 0 && (
                <Button 
                  variant="outline" 
                  className="w-full border-slate-600"
                  onClick={onClear}
                >
                  Vider le panier
                </Button>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default CartWidget;
