/**
 * OrderCard - Order display card component
 * Phase 9 - Business Modules
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Clock, Check, Settings, Package, CheckCircle, XCircle, RefreshCcw, Link, ClipboardList, Truck } from 'lucide-react';

const STATUS_ICONS = {
  pending: Clock,
  confirmed: Check,
  processing: Settings,
  shipped: Package,
  delivered: CheckCircle,
  cancelled: XCircle,
  refunded: RefreshCcw
};

const MODE_ICONS = {
  dropshipping: Truck,
  affiliate: Link,
  direct: Package
};

export const OrderCard = ({ order, onViewDetails, onCancel, compact = false }) => {
  if (!order) return null;

  const getStatusInfo = (status) => {
    const statusMap = {
      pending: { color: 'amber', label: 'En attente' },
      confirmed: { color: 'blue', label: 'Confirmée' },
      processing: { color: 'purple', label: 'En traitement' },
      shipped: { color: 'cyan', label: 'Expédiée' },
      delivered: { color: 'emerald', label: 'Livrée' },
      cancelled: { color: 'red', label: 'Annulée' },
      refunded: { color: 'slate', label: 'Remboursée' }
    };
    return statusMap[status] || { color: 'slate', label: status };
  };

  const getSaleModeInfo = (mode) => {
    const modes = {
      dropshipping: { label: 'Dropshipping' },
      affiliate: { label: 'Affiliation' },
      direct: { label: 'Vente directe' }
    };
    return modes[mode] || { label: mode };
  };

  const statusInfo = getStatusInfo(order.status);
  const modeInfo = getSaleModeInfo(order.sale_mode);
  const StatusIcon = STATUS_ICONS[order.status] || ClipboardList;
  const ModeIcon = MODE_ICONS[order.sale_mode] || ClipboardList;

  if (compact) {
    return (
      <div className="flex items-center justify-between bg-slate-800 rounded-lg p-3 border border-slate-700">
        <div className="flex items-center gap-3">
          <StatusIcon className="h-5 w-5" />
          <div>
            <p className="text-white text-sm font-medium">#{order.order_number || order.id?.slice(-8)}</p>
            <p className="text-slate-400 text-xs">{order.total?.toFixed(2)}$</p>
          </div>
        </div>
        <Badge className={`bg-${statusInfo.color}-900/50 text-${statusInfo.color}-400`}>
          {statusInfo.label}
        </Badge>
      </div>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-white font-semibold">
              Commande #{order.order_number || order.id?.slice(-8)}
            </p>
            <p className="text-slate-400 text-sm">
              {order.created_at && new Date(order.created_at).toLocaleDateString('fr-CA')}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge className={`bg-${statusInfo.color}-900/50 text-${statusInfo.color}-400 flex items-center gap-1`}>
              <StatusIcon className="h-3 w-3" /> {statusInfo.label}
            </Badge>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <ModeIcon className="h-3 w-3" /> {modeInfo.label}
            </span>
          </div>
        </div>

        {/* Items */}
        {order.items && order.items.length > 0 && (
          <div className="space-y-2 mb-4">
            {order.items.slice(0, 3).map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-slate-300 truncate flex-1">
                  {item.product_name || item.name} × {item.quantity}
                </span>
                <span className="text-white ml-2">
                  {(item.price * item.quantity).toFixed(2)}$
                </span>
              </div>
            ))}
            {order.items.length > 3 && (
              <p className="text-slate-500 text-xs">+{order.items.length - 3} autres articles</p>
            )}
          </div>
        )}

        {/* Total */}
        <div className="flex justify-between items-center pt-3 border-t border-slate-700">
          <span className="text-slate-400">Total</span>
          <span className="text-[#f5a623] font-bold text-lg">
            {order.total?.toFixed(2)}$
          </span>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-4">
          {onViewDetails && (
            <Button 
              variant="outline" 
              size="sm" 
              className="flex-1 border-slate-600"
              onClick={() => onViewDetails(order)}
            >
              Voir détails
            </Button>
          )}
          {onCancel && order.status === 'pending' && (
            <Button 
              variant="outline" 
              size="sm"
              className="border-red-700 text-red-400 hover:bg-red-900/30"
              onClick={() => onCancel(order)}
            >
              Annuler
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default OrderCard;
