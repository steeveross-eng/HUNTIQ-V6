/**
 * PropertySourceBadge - Badge indicating property source
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { Badge } from '../../../components/ui/badge';
import { Globe, Home, Store, Building, Users } from 'lucide-react';

const SOURCE_CONFIG = {
  centris: {
    label: 'Centris',
    Icon: Building,
    className: 'bg-blue-900/50 text-blue-400 border-blue-700'
  },
  duproprio: {
    label: 'DuProprio',
    Icon: Home,
    className: 'bg-green-900/50 text-green-400 border-green-700'
  },
  kijiji: {
    label: 'Kijiji',
    Icon: Store,
    className: 'bg-purple-900/50 text-purple-400 border-purple-700'
  },
  manual: {
    label: 'Manuel',
    Icon: Users,
    className: 'bg-slate-700/50 text-slate-400 border-slate-600'
  },
  api_b2b: {
    label: 'API B2B',
    Icon: Globe,
    className: 'bg-amber-900/50 text-amber-400 border-amber-700'
  }
};

/**
 * Property Source Badge Component
 * 
 * @param {Object} props
 * @param {string} props.source - Source identifier
 * @param {string} props.className - Additional CSS classes
 */
const PropertySourceBadge = ({ 
  source = 'manual',
  className = ''
}) => {
  const config = SOURCE_CONFIG[source] || SOURCE_CONFIG.manual;
  const { label, Icon, className: badgeClass } = config;

  return (
    <Badge className={`${badgeClass} ${className} border text-xs`}>
      <Icon className="w-3 h-3 mr-1" />
      {label}
    </Badge>
  );
};

export default PropertySourceBadge;
