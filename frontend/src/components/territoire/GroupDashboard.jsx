/**
 * GroupDashboard - Tableau de bord du groupe de chasse avec tracking live et chat
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMap } from 'react-leaflet';
import { 
  Users, MapPin, MessageCircle, Radio, Power, Send, 
  AlertTriangle, Navigation, Clock, ChevronDown, ChevronUp,
  Settings, Eye, EyeOff, RefreshCw, X, Maximize2, Minimize2,
  User, Compass, Target, Zap, Coffee, Home, HelpCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useLiveTracking, useGroupChat } from '@/hooks/useLiveTracking';
import L from 'leaflet';
import { toast } from 'sonner';

// Couleurs pour les membres (jusqu'à 10)
const MEMBER_COLORS = [
  '#f5a623', '#22c55e', '#3b82f6', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
];

// Icônes d'alerte - BIONIC Design System Compliant (uses lucide-react)
const ALERT_ICONS = {
  animal_spotted: 'target',
  position_marked: 'map-pin',
  need_help: 'alert-triangle',
  shot_fired: 'crosshair',
  returning: 'home',
  break_time: 'coffee',
  silence: 'volume-x',
  meeting_point: 'users'
};

// Créer une icône personnalisée pour un membre
const createMemberIcon = (color, name) => {
  const initial = name ? name.charAt(0).toUpperCase() : '?';
  return L.divIcon({
    className: 'custom-member-marker',
    html: `
      <div style="
        width: 36px; 
        height: 36px; 
        background: ${color}; 
        border-radius: 50%; 
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
      ">${initial}</div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18]
  });
};

// Composant pour centrer la carte
const MapCenterController = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [center, zoom, map]);
  return null;
};

/**
 * GroupDashboard principal
 */
export const GroupDashboard = ({ 
  group, 
  userId, 
  onClose,
  initialTab = 'map'
}) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [showSettings, setShowSettings] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedMember, setSelectedMember] = useState(null);
  const [showTrail, setShowTrail] = useState({});
  const [memberTrails, setMemberTrails] = useState({});
  const [chatMessage, setChatMessage] = useState('');
  const [mapCenter, setMapCenter] = useState([46.8139, -71.2080]);
  
  const chatScrollRef = useRef(null);
  const messageInputRef = useRef(null);

  // Hooks de tracking et chat
  const {
    isTracking,
    trackingMode,
    shareExactPosition,
    membersPositions,
    myPosition,
    loading: trackingLoading,
    startTracking,
    stopTracking,
    sendManualPosition,
    getPositionHistory,
    updateSettings,
    setTrackingMode,
    setShareExactPosition,
    refreshPositions
  } = useLiveTracking(userId, group?.id, {
    updateInterval: 30000,
    onMemberUpdate: (members) => {
      // Centrer sur le groupe si première position
      if (members.length > 0 && !mapCenter) {
        const avgLat = members.reduce((s, m) => s + m.lat, 0) / members.length;
        const avgLng = members.reduce((s, m) => s + m.lng, 0) / members.length;
        setMapCenter([avgLat, avgLng]);
      }
    }
  });

  const {
    messages,
    unreadCount,
    isConnected,
    alertTypes,
    quickMessages,
    vibrationEnabled,
    sendMessage,
    sendAlert,
    markAsRead,
    sendTyping,
    toggleVibration
  } = useGroupChat(userId, group?.id, {
    onAlert: (msg) => {
      toast.warning(msg.content, {
        description: `De ${msg.sender_name}`
      });
    }
  });

  // Scroll auto pour le chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Marquer comme lu quand on ouvre le chat
  useEffect(() => {
    if (activeTab === 'chat' && unreadCount > 0) {
      markAsRead();
    }
  }, [activeTab, unreadCount, markAsRead]);

  // Charger le trajet d'un membre
  const loadMemberTrail = useCallback(async (memberId) => {
    const positions = await getPositionHistory(memberId, 6);
    setMemberTrails(prev => ({
      ...prev,
      [memberId]: positions.map(p => [p.lat, p.lng])
    }));
  }, [getPositionHistory]);

  // Toggle affichage du trajet
  const toggleTrail = useCallback((memberId) => {
    setShowTrail(prev => {
      const newShow = !prev[memberId];
      if (newShow && !memberTrails[memberId]) {
        loadMemberTrail(memberId);
      }
      return { ...prev, [memberId]: newShow };
    });
  }, [memberTrails, loadMemberTrail]);

  // Envoyer un message
  const handleSendMessage = useCallback(async (e) => {
    e?.preventDefault();
    if (!chatMessage.trim()) return;
    
    await sendMessage(chatMessage);
    setChatMessage('');
    messageInputRef.current?.focus();
  }, [chatMessage, sendMessage]);

  // Envoyer un message rapide
  const handleQuickMessage = useCallback((text) => {
    sendMessage(text);
  }, [sendMessage]);

  // Envoyer une alerte
  const handleSendAlert = useCallback((alertType) => {
    const location = myPosition ? { lat: myPosition.lat, lng: myPosition.lng } : null;
    sendAlert(alertType, null, location);
  }, [sendAlert, myPosition]);

  // Centrer sur un membre
  const centerOnMember = useCallback((member) => {
    setMapCenter([member.lat, member.lng]);
    setSelectedMember(member);
  }, []);

  if (!group) return null;

  // Assigner des couleurs aux membres
  const membersWithColors = membersPositions.map((member, index) => ({
    ...member,
    color: MEMBER_COLORS[index % MEMBER_COLORS.length],
    isMe: member.user_id === userId
  }));

  return (
    <div className={`bg-gray-900 border border-gray-700 rounded-xl overflow-hidden shadow-2xl ${isExpanded ? 'w-full h-full' : 'w-80'}`}>
      {/* Header */}
      <div className="bg-gray-800 px-4 py-3 flex items-center justify-between border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Users className="h-5 w-5 text-[#f5a623]" />
          <div>
            <h3 className="font-semibold text-white">{group.name}</h3>
            <p className="text-xs text-gray-400">
              {membersPositions.length} membre{membersPositions.length > 1 ? 's' : ''} en ligne
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Toggle tracking */}
          <Button
            size="sm"
            variant={isTracking ? "default" : "outline"}
            onClick={isTracking ? stopTracking : startTracking}
            className={isTracking ? 'bg-green-600 hover:bg-green-700' : 'border-gray-600'}
            disabled={trackingLoading}
          >
            <Power className={`h-4 w-4 mr-1 ${isTracking ? 'text-white' : ''}`} />
            {isTracking ? 'ON' : 'OFF'}
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400"
          >
            {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="text-gray-400"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Onglets */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-[calc(100%-60px)]">
        <TabsList className="bg-gray-800/50 border-b border-gray-700 rounded-none p-1">
          <TabsTrigger value="map" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <MapPin className="h-4 w-4 mr-1" />
            Carte
          </TabsTrigger>
          <TabsTrigger value="members" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Users className="h-4 w-4 mr-1" />
            Membres
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black relative">
            <MessageCircle className="h-4 w-4 mr-1" />
            Chat
            {unreadCount > 0 && (
              <Badge className="absolute -top-1 -right-1 bg-red-500 text-white text-xs h-5 w-5 p-0 flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Onglet Carte */}
        <TabsContent value="map" className="flex-1 m-0 relative">
          <MapContainer 
            center={mapCenter} 
            zoom={13} 
            className="h-full w-full"
            zoomControl={false}
          >
            <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
            <MapCenterController center={mapCenter} />
            
            {/* Marqueurs des membres */}
            {membersWithColors.map(member => (
              <React.Fragment key={member.user_id}>
                <Marker
                  position={[member.lat, member.lng]}
                  icon={createMemberIcon(member.color, member.name)}
                  eventHandlers={{
                    click: () => setSelectedMember(member)
                  }}
                >
                  <Popup>
                    <div className="text-center min-w-[150px]">
                      <div className="font-bold" style={{ color: member.color }}>
                        {member.name} {member.isMe && '(Vous)'}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {member.is_online ? (
                          <span className="text-green-600">● En ligne</span>
                        ) : (
                          <span className="text-gray-500">● Hors ligne</span>
                        )}
                      </div>
                      {member.distance_km && (
                        <div className="text-sm mt-1 flex items-center gap-1">
                          <MapPin className="h-3 w-3" /> {member.distance_km < 1 
                            ? `${Math.round(member.distance_km * 1000)} m` 
                            : `${member.distance_km.toFixed(1)} km`
                          }
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">
                        Mis à jour: {new Date(member.last_update).toLocaleTimeString('fr-FR')}
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-2 text-xs"
                        onClick={() => toggleTrail(member.user_id)}
                      >
                        {showTrail[member.user_id] ? 'Masquer trajet' : 'Voir trajet'}
                      </Button>
                    </div>
                  </Popup>
                </Marker>
                
                {/* Cercle de précision */}
                {member.accuracy && (
                  <Circle
                    center={[member.lat, member.lng]}
                    radius={member.accuracy}
                    pathOptions={{
                      color: member.color,
                      fillColor: member.color,
                      fillOpacity: 0.1,
                      weight: 1
                    }}
                  />
                )}
                
                {/* Trajet */}
                {showTrail[member.user_id] && memberTrails[member.user_id] && (
                  <Polyline
                    positions={memberTrails[member.user_id]}
                    pathOptions={{
                      color: member.color,
                      weight: 3,
                      opacity: 0.7,
                      dashArray: '5, 10'
                    }}
                  />
                )}
              </React.Fragment>
            ))}
          </MapContainer>

          {/* Contrôles carte */}
          <div className="absolute bottom-4 left-4 z-[1000] flex flex-col gap-2">
            <Button
              size="sm"
              onClick={refreshPositions}
              className="bg-black/80 text-white border border-gray-700"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            {trackingMode === 'manual' && isTracking && (
              <Button
                size="sm"
                onClick={sendManualPosition}
                className="bg-[#f5a623] text-black"
              >
                <Navigation className="h-4 w-4 mr-1" />
                Envoyer ma position
              </Button>
            )}
          </div>

          {/* Légende */}
          <div className="absolute top-4 right-4 z-[1000] bg-black/80 rounded-lg p-3 border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Membres</div>
            <div className="space-y-1">
              {membersWithColors.slice(0, 5).map(member => (
                <div 
                  key={member.user_id}
                  className="flex items-center gap-2 cursor-pointer hover:bg-gray-800/50 p-1 rounded"
                  onClick={() => centerOnMember(member)}
                >
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: member.color }}
                  />
                  <span className="text-xs text-white truncate max-w-[100px]">
                    {member.name} {member.isMe && '(Vous)'}
                  </span>
                  {member.is_online && (
                    <span className="w-2 h-2 bg-green-500 rounded-full" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        {/* Onglet Membres */}
        <TabsContent value="members" className="flex-1 m-0 overflow-auto p-4">
          <div className="space-y-3">
            {membersWithColors.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Aucun membre en tracking</p>
                <p className="text-xs mt-1">Activez le tracking pour voir les membres</p>
              </div>
            ) : (
              membersWithColors.map(member => (
                <Card 
                  key={member.user_id}
                  className={`bg-gray-800/50 border-gray-700 cursor-pointer hover:bg-gray-700/50 transition-colors ${
                    member.isMe ? 'ring-2 ring-[#f5a623]' : ''
                  }`}
                  onClick={() => {
                    centerOnMember(member);
                    setActiveTab('map');
                  }}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                          style={{ backgroundColor: member.color }}
                        >
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-white">
                            {member.name} {member.isMe && <Badge className="ml-1 bg-[#f5a623] text-black text-xs">Vous</Badge>}
                          </div>
                          <div className="text-xs text-gray-400 flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${member.is_online ? 'bg-green-500' : 'bg-gray-500'}`} />
                            {member.is_online ? 'En ligne' : 'Hors ligne'}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        {member.distance_km && !member.isMe && (
                          <div className="text-sm text-[#f5a623] font-medium">
                            {member.distance_km < 1 
                              ? `${Math.round(member.distance_km * 1000)} m` 
                              : `${member.distance_km.toFixed(1)} km`
                            }
                          </div>
                        )}
                        <div className="text-xs text-gray-500">
                          {new Date(member.last_update).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Onglet Chat */}
        <TabsContent value="chat" className="flex-1 m-0 flex flex-col">
          {/* Messages */}
          <ScrollArea ref={chatScrollRef} className="flex-1 p-4">
            <div className="space-y-3">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Aucun message</p>
                  <p className="text-xs mt-1">Commencez la conversation !</p>
                </div>
              ) : (
                messages.map(msg => (
                  <div 
                    key={msg.id}
                    className={`flex ${msg.sender_id === userId ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${
                      msg.message_type === 'alert' 
                        ? 'bg-red-900/50 border border-red-700' 
                        : msg.sender_id === userId 
                          ? 'bg-[#f5a623] text-black' 
                          : 'bg-gray-800'
                    } rounded-lg p-3`}>
                      {msg.sender_id !== userId && (
                        <div className="text-xs text-gray-400 mb-1">{msg.sender_name}</div>
                      )}
                      <div className={msg.sender_id === userId ? 'text-black' : 'text-white'}>
                        {msg.content}
                      </div>
                      <div className={`text-xs mt-1 ${
                        msg.sender_id === userId ? 'text-black/60' : 'text-gray-500'
                      }`}>
                        {new Date(msg.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>

          {/* Alertes rapides + Toggle vibration */}
          <div className="border-t border-gray-700 p-2 bg-gray-800/50">
            <div className="flex items-center justify-between mb-2">
              <div className="flex gap-1 overflow-x-auto flex-1">
                {Object.entries(alertTypes).slice(0, 6).map(([key, info]) => (
                  <Button
                    key={key}
                    size="sm"
                    variant="outline"
                    onClick={() => handleSendAlert(key)}
                    className={`border-gray-600 text-xs whitespace-nowrap ${
                      info.vibrate ? 'hover:bg-red-900/50 hover:border-red-700' : ''
                    }`}
                  >
                    {info.emoji}
                  </Button>
                ))}
              </div>
              {/* Toggle Vibration ON/OFF */}
              <div className="flex items-center gap-2 ml-2 pl-2 border-l border-gray-700">
                <button
                  onClick={() => toggleVibration(!vibrationEnabled)}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                    vibrationEnabled 
                      ? 'bg-green-600/20 text-green-400 border border-green-600/50' 
                      : 'bg-gray-700/50 text-gray-500 border border-gray-600'
                  }`}
                  title={vibrationEnabled ? 'Vibrations activées' : 'Vibrations désactivées'}
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    className="h-4 w-4"
                  >
                    <path d="M2 8h2a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H2V8z"/>
                    <path d="M6 8h12a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H6V8z"/>
                    <path d="M20 8h2v8h-2"/>
                    {!vibrationEnabled && <path d="M2 2l20 20" className="text-red-500"/>}
                  </svg>
                  <span className="hidden sm:inline">{vibrationEnabled ? 'ON' : 'OFF'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Input message */}
          <form onSubmit={handleSendMessage} className="border-t border-gray-700 p-3 bg-gray-800">
            <div className="flex gap-2">
              <Input
                ref={messageInputRef}
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={() => sendTyping()}
                placeholder="Message..."
                className="bg-gray-900 border-gray-700 text-white"
              />
              <Button 
                type="submit" 
                disabled={!chatMessage.trim()}
                className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </TabsContent>
      </Tabs>

      {/* Paramètres */}
      {showSettings && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-50">
          <Card className="w-80 bg-gray-900 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white">Paramètres tracking</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => setShowSettings(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-white">Mode tracking</div>
                  <div className="text-xs text-gray-500">
                    {trackingMode === 'auto' ? 'Automatique (30s)' : 'Manuel (bouton)'}
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const newMode = trackingMode === 'auto' ? 'manual' : 'auto';
                    setTrackingMode(newMode);
                    updateSettings({ mode: newMode });
                  }}
                >
                  {trackingMode === 'auto' ? 'Auto' : 'Manuel'}
                </Button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-white">Position exacte</div>
                  <div className="text-xs text-gray-500">
                    {shareExactPosition ? 'Précise' : 'Approximative (~100m)'}
                  </div>
                </div>
                <Switch
                  checked={shareExactPosition}
                  onCheckedChange={(checked) => {
                    setShareExactPosition(checked);
                    updateSettings({ share_exact_position: checked });
                  }}
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default GroupDashboard;
