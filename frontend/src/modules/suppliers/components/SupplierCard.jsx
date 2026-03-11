/**
 * SupplierCard - Supplier display card
 * Phase 9 - Business Modules
 * BIONIC Design System compliant - No emojis
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Factory, Truck, Store, Package, Building2, Mail, DollarSign } from 'lucide-react';

const TYPE_ICONS = {
  manufacturer: Factory,
  distributor: Truck,
  retailer: Store,
  dropshipper: Package,
  default: Building2
};

export const SupplierCard = ({ supplier, onSelect, compact = false }) => {
  if (!supplier) return null;

  const getTypeInfo = (type) => {
    const types = {
      manufacturer: { label: 'Fabricant', color: 'blue' },
      distributor: { label: 'Distributeur', color: 'purple' },
      retailer: { label: 'Détaillant', color: 'emerald' },
      dropshipper: { label: 'Dropshipper', color: 'amber' }
    };
    return types[type] || { label: type, color: 'slate' };
  };
  
  const TypeIcon = TYPE_ICONS[supplier.type] || TYPE_ICONS.default;

  const typeInfo = getTypeInfo(supplier.type);

  if (compact) {
    return (
      <div 
        className="flex items-center gap-3 bg-slate-800 rounded-lg p-3 border border-slate-700 cursor-pointer hover:border-slate-500"
        onClick={() => onSelect?.(supplier)}
      >
        <TypeIcon className="w-5 h-5 text-slate-300" />
        <div className="flex-1">
          <p className="text-white text-sm font-medium">{supplier.name}</p>
          <p className="text-slate-400 text-xs">{typeInfo.label}</p>
        </div>
        <Badge className={`${supplier.is_active ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}>
          {supplier.is_active ? 'Actif' : 'Inactif'}
        </Badge>
      </div>
    );
  }

  return (
    <Card 
      className="bg-slate-800 border-slate-700 cursor-pointer hover:border-slate-500 transition-colors"
      onClick={() => onSelect?.(supplier)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <TypeIcon className="w-6 h-6 text-slate-300" />
            <div>
              <h3 className="text-white font-semibold">{supplier.name}</h3>
              <Badge className={`bg-${typeInfo.color}-900/50 text-${typeInfo.color}-400 text-xs`}>
                {typeInfo.label}
              </Badge>
            </div>
          </div>
          <Badge className={`${supplier.is_active ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}>
            {supplier.is_active ? 'Actif' : 'Inactif'}
          </Badge>
        </div>

        {supplier.contact_email && (
          <p className="text-slate-400 text-sm mb-2 flex items-center gap-2">
            <Mail className="w-4 h-4" /> {supplier.contact_email}
          </p>
        )}

        {supplier.products_count !== undefined && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-300 flex items-center gap-1">
              <Package className="w-4 h-4" /> {supplier.products_count} produits
            </span>
            {supplier.commission_rate && (
              <span className="text-amber-400 flex items-center gap-1">
                <DollarSign className="w-4 h-4" /> {supplier.commission_rate}% commission
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SupplierCard;
