/**
 * OrdersList - Orders list component
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { OrderCard } from './OrderCard';
import { ClipboardList } from 'lucide-react';

export const OrdersList = ({ 
  orders = [], 
  onViewDetails, 
  onCancel,
  loading = false,
  emptyMessage = 'Aucune commande'
}) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse bg-slate-800 rounded-lg p-4">
            <div className="flex justify-between mb-4">
              <div className="h-5 bg-slate-700 rounded w-32" />
              <div className="h-5 bg-slate-700 rounded w-24" />
            </div>
            <div className="space-y-2 mb-4">
              <div className="h-4 bg-slate-700 rounded w-full" />
              <div className="h-4 bg-slate-700 rounded w-3/4" />
            </div>
            <div className="h-6 bg-slate-700 rounded w-24 ml-auto" />
          </div>
        ))}
      </div>
    );
  }

  if (!orders.length) {
    return (
      <div className="text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
        <ClipboardList className="w-16 h-16 text-slate-500 mx-auto" />
        <p className="text-slate-400 mt-4">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <OrderCard
          key={order.id}
          order={order}
          onViewDetails={onViewDetails}
          onCancel={onCancel}
        />
      ))}
    </div>
  );
};

export default OrdersList;
