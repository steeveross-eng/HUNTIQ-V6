/**
 * CartModals.jsx — Shopping Cart + Order Form Modals
 * 
 * Cart displays items with quantity controls and total.
 * Order form collects customer info and submits the order.
 * 
 * Phase 3 extraction from TerritoryMap.jsx
 * @module territory/CartModals
 */

import React from 'react';
import { ShoppingCart, Trash2, Send, Package, RefreshCw, Check, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Label } from '../ui/label';
import { Input } from '../ui/input';

// Cart Modal
export const CartModal = ({
  show, cart, onClose, removeFromCart, updateCartQuantity,
  getCartTotal, onShowOrderForm,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-[2000] flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-card border-b border-border p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-[#f5a623]" />
            <h2 className="text-white text-lg font-bold">Panier BIONIC</h2>
            <Badge className="bg-[#f5a623] text-black">{cart.reduce((sum, item) => sum + item.quantity, 0)}</Badge>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto max-h-[50vh]">
          {cart.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingCart className="h-12 w-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">Votre panier est vide</p>
              <p className="text-gray-500 text-sm mt-1">Ajoutez des produits depuis l'analyse nutritionnelle</p>
            </div>
          ) : (
            <div className="space-y-3">
              {cart.map((item) => (
                <div key={item.id} className="bg-background rounded-lg p-3 border border-border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-white font-medium text-sm">{item.name}</h4>
                        {item.is_bionic && (
                          <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC</Badge>
                        )}
                      </div>
                      <p className="text-gray-400 text-xs">{item.category}</p>
                    </div>
                    <button onClick={() => removeFromCart(item.id)} className="text-red-400 hover:text-red-300">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateCartQuantity(item.id, -1)}
                        className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
                      >
                        <span className="text-white text-sm">-</span>
                      </button>
                      <span className="text-white w-8 text-center">{item.quantity}</span>
                      <button
                        onClick={() => updateCartQuantity(item.id, 1)}
                        className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
                      >
                        <span className="text-white text-sm">+</span>
                      </button>
                    </div>
                    <span className="text-[#f5a623] font-bold">${(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart.length > 0 && (
          <div className="border-t border-border p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Total</span>
              <span className="text-white text-xl font-bold">${getCartTotal().toFixed(2)} CAD</span>
            </div>
            <Button className="w-full btn-golden text-black" onClick={onShowOrderForm}>
              <Send className="h-4 w-4 mr-2" />
              Commander (approbation requise)
            </Button>
            <p className="text-xs text-gray-500 text-center">
              La commande sera envoyee a l'administrateur pour approbation
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Order Form Modal
export const OrderFormModal = ({
  show, cart, onClose, getCartTotal,
  orderName, setOrderName, orderEmail, setOrderEmail,
  orderPhone, setOrderPhone, orderNotes, setOrderNotes,
  onSubmit, submitting,
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-[2001] flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-border">
          <h2 className="text-white text-lg font-bold flex items-center gap-2">
            <Package className="h-5 w-5 text-[#f5a623]" />
            Formulaire de commande
          </h2>
          <p className="text-gray-400 text-sm">Remplissez vos informations pour soumettre la commande</p>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <Label className="text-gray-400 text-xs">Nom complet *</Label>
            <Input value={orderName} onChange={(e) => setOrderName(e.target.value)} placeholder="Jean Tremblay" className="bg-background border-border mt-1" />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Email *</Label>
            <Input type="email" value={orderEmail} onChange={(e) => setOrderEmail(e.target.value)} placeholder="jean@exemple.com" className="bg-background border-border mt-1" />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Telephone</Label>
            <Input value={orderPhone} onChange={(e) => setOrderPhone(e.target.value)} placeholder="(418) 555-1234" className="bg-background border-border mt-1" />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Notes / Instructions speciales</Label>
            <textarea value={orderNotes} onChange={(e) => setOrderNotes(e.target.value)} placeholder="Instructions de livraison, etc." className="w-full bg-background border border-border rounded-md p-2 mt-1 text-white text-sm resize-none h-20" />
          </div>

          {/* Order Summary */}
          <div className="bg-background rounded-lg p-3 border border-border">
            <p className="text-gray-400 text-xs mb-2">Resume de la commande</p>
            <div className="space-y-1">
              {cart.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-300">{item.name} x{item.quantity}</span>
                  <span className="text-white">${(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-border mt-2 pt-2 flex justify-between">
              <span className="text-white font-medium">Total</span>
              <span className="text-[#f5a623] font-bold">${getCartTotal().toFixed(2)} CAD</span>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-border flex gap-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Annuler
          </Button>
          <Button
            className="flex-1 btn-golden text-black"
            onClick={onSubmit}
            disabled={submitting || !orderName || !orderEmail}
          >
            {submitting ? (
              <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Envoi...</>
            ) : (
              <><Check className="h-4 w-4 mr-2" /> Soumettre</>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
