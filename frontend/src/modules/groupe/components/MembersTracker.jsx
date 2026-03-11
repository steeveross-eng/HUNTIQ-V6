/**
 * MembersTracker - Composant d'affichage des positions membres sur la carte
 * BIONIC Design System compliant
 * Version: 1.0.0 - Phase 3
 * 
 * Affiche les markers des membres du groupe sur une carte Leaflet
 */
import React, { useMemo, useCallback } from 'react';
import { Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useLanguage } from '../../../contexts/LanguageContext';
import { TRACKING_STATUS } from '../hooks/useGroupeTracking';
import { 
  Target, Navigation, Binoculars, Coffee, AlertTriangle,
  Clock, Crosshair, Radio
} from 'lucide-react';

// Status icon mapping
const STATUS_ICONS = {
  hunting: Target,
  moving: Navigation,
  observing: Binoculars,
  break: Coffee,
  emergency: AlertTriangle
};

// Create custom marker icon for member
const createMemberIcon = (member) => {
  const statusConfig = TRACKING_STATUS[member.status] || TRACKING_STATUS.moving;
  const isOnline = member.isOnline;
  const isRecent = member.isRecent;
  
  // Determine border color based on online status
  let borderColor = '#6b7280'; // Gray for offline
  if (isOnline) {
    borderColor = '#10b981'; // Green for online
  } else if (isRecent) {
    borderColor = '#f5a623'; // Gold for recent
  }
  
  // Get status color from CSS variable (fallback to hex)
  const statusColor = member.status === 'hunting' ? '#f5a623' :
                      member.status === 'moving' ? '#60a5fa' :
                      member.status === 'observing' ? '#10b981' :
                      member.status === 'break' ? '#9ca3af' :
                      member.status === 'emergency' ? '#ef4444' : '#f5a623';
  
  // SVG icon based on status
  const iconSvg = member.status === 'hunting' 
    ? '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" fill="none" stroke-width="1.5"/>'
    : member.status === 'observing'
    ? '<circle cx="6" cy="10" r="2"/><circle cx="18" cy="10" r="2"/><path d="M21 10c0 0-4 6-9 6s-9-6-9-6"/>'
    : member.status === 'emergency'
    ? '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'
    : '<polygon points="3 11 22 2 13 21 11 13 3 11"/>';
  
  const iconHtml = `
    <div style="
      position: relative;
      width: 36px;
      height: 36px;
    ">
      <div style="
        background-color: ${statusColor};
        width: 32px;
        height: 32px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid ${borderColor};
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        position: absolute;
        top: 0;
        left: 0;
      ">
        <div style="transform: rotate(45deg);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            ${iconSvg}
          </svg>
        </div>
      </div>
      ${isOnline ? `
        <div style="
          position: absolute;
          top: -2px;
          right: -2px;
          width: 10px;
          height: 10px;
          background-color: #10b981;
          border-radius: 50%;
          border: 2px solid #1a1a2e;
          animation: pulse 2s infinite;
        "></div>
      ` : ''}
    </div>
    <style>
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
    </style>
  `;
  
  return L.divIcon({
    html: iconHtml,
    className: 'member-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
  });
};

// Create accuracy circle style
const getAccuracyCircleStyle = (member) => {
  const isOnline = member.isOnline;
  
  return {
    color: isOnline ? '#10b981' : '#f5a623',
    fillColor: isOnline ? '#10b98130' : '#f5a62320',
    fillOpacity: 0.3,
    weight: 1,
    dashArray: isOnline ? null : '5, 5'
  };
};

// Member Marker Component
const MemberMarker = ({ member, onCenterMap, showAccuracy = true, showTrail = false, trail = [] }) => {
  const { t } = useLanguage();
  
  // Memoize icon before any conditional returns
  const icon = useMemo(() => {
    if (!member.position || !member.position.lat || !member.position.lng) {
      return null;
    }
    return createMemberIcon(member);
  }, [member]);
  
  // Early return if no valid position
  if (!member.position || !member.position.lat || !member.position.lng) {
    return null;
  }
  
  const position = [member.position.lat, member.position.lng];
  const StatusIcon = STATUS_ICONS[member.status] || Navigation;
  
  return (
    <>
      {/* Accuracy circle */}
      {showAccuracy && member.accuracy && member.accuracy < 500 && (
        <Circle
          center={position}
          radius={member.accuracy}
          pathOptions={getAccuracyCircleStyle(member)}
        />
      )}
      
      {/* Trail polyline */}
      {showTrail && trail.length > 1 && (
        <Polyline
          positions={trail.map(p => [p.lat, p.lng])}
          pathOptions={{
            color: member.isOnline ? '#10b981' : '#6b7280',
            weight: 2,
            opacity: 0.6,
            dashArray: '5, 10'
          }}
        />
      )}
      
      {/* Member marker */}
      <Marker 
        position={position} 
        icon={icon}
        eventHandlers={{
          click: () => onCenterMap?.(member.id)
        }}
      >
        <Popup className="bionic-popup">
          <div className="min-w-[180px] p-2">
            {/* Header */}
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-gray-700">
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
                style={{ backgroundColor: member.statusConfig?.colorVar || '#f5a623' }}
              >
                {member.name?.charAt(0) || '?'}
              </div>
              <div>
                <div className="font-semibold text-white text-sm">{member.name}</div>
                <div className="flex items-center gap-1 text-xs">
                  <span 
                    className={`w-2 h-2 rounded-full ${member.isOnline ? 'bg-green-500' : member.isRecent ? 'bg-yellow-500' : 'bg-gray-500'}`}
                  />
                  <span className="text-gray-400">
                    {member.isOnline ? t('groupe_member_online') : member.timeSince}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Status */}
            <div className="flex items-center gap-2 mb-2">
              <StatusIcon 
                className="h-4 w-4" 
                style={{ color: member.statusConfig?.colorVar || '#f5a623' }}
              />
              <span className="text-sm text-gray-300">{t(member.statusConfig?.labelKey || 'groupe_status_moving')}</span>
            </div>
            
            {/* Position info */}
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex items-center gap-1">
                <Crosshair className="h-3 w-3" />
                <span>{member.position.lat.toFixed(5)}, {member.position.lng.toFixed(5)}</span>
              </div>
              {member.accuracy && (
                <div className="flex items-center gap-1">
                  <Radio className="h-3 w-3" />
                  <span>±{Math.round(member.accuracy)}m</span>
                </div>
              )}
              {member.speed && member.speed > 0 && (
                <div className="flex items-center gap-1">
                  <Navigation className="h-3 w-3" />
                  <span>{(member.speed * 3.6).toFixed(1)} km/h</span>
                </div>
              )}
            </div>
          </div>
        </Popup>
      </Marker>
    </>
  );
};

// Map controller to center on member
const CenterOnMember = ({ position, zoom = 15 }) => {
  const map = useMap();
  
  React.useEffect(() => {
    if (position) {
      map.flyTo(position, zoom, { duration: 0.5 });
    }
  }, [map, position, zoom]);
  
  return null;
};

// Main MembersTracker component
export const MembersTracker = ({ 
  members = [],
  currentUserId = null,
  showAccuracy = true,
  showTrails = false,
  memberTrails = {},
  onCenterMap = null,
  centerOnMemberId = null,
  excludeSelf = true
}) => {
  const { t } = useLanguage();
  
  // Filter members to display
  const displayMembers = useMemo(() => {
    let filtered = members.filter(m => m.position && m.position.lat && m.position.lng);
    
    if (excludeSelf && currentUserId) {
      filtered = filtered.filter(m => m.id !== currentUserId);
    }
    
    return filtered;
  }, [members, currentUserId, excludeSelf]);
  
  // Get center position for centering
  const centerPosition = useMemo(() => {
    if (!centerOnMemberId) return null;
    
    const member = members.find(m => m.id === centerOnMemberId);
    if (member?.position) {
      return [member.position.lat, member.position.lng];
    }
    return null;
  }, [centerOnMemberId, members]);
  
  // Handle center on member click
  const handleCenterMap = useCallback((memberId) => {
    if (onCenterMap) {
      onCenterMap(memberId);
    }
  }, [onCenterMap]);
  
  return (
    <>
      {/* Center controller */}
      {centerPosition && (
        <CenterOnMember position={centerPosition} />
      )}
      
      {/* Member markers */}
      {displayMembers.map(member => (
        <MemberMarker
          key={member.id}
          member={member}
          onCenterMap={handleCenterMap}
          showAccuracy={showAccuracy}
          showTrail={showTrails}
          trail={memberTrails[member.id] || []}
        />
      ))}
    </>
  );
};

export default MembersTracker;
