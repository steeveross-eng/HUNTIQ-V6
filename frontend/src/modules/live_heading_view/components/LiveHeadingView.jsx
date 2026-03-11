/**
 * LiveHeadingView - Main Component
 * Immersive map view with heading-based navigation
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { CompassWidget } from './CompassWidget';
import { WindIndicator } from './WindIndicator';
import { POIMarker } from './POIMarker';
import { AlertToast } from './AlertToast';
import { SessionControls } from './SessionControls';
import { SessionStats } from './SessionStats';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const LiveHeadingView = ({ userId = 'demo_user', onClose }) => {
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [sessionState, setSessionState] = useState('initializing');
  const [position, setPosition] = useState(null);
  const [heading, setHeading] = useState(0);
  const [viewCone, setViewCone] = useState(null);
  const [wind, setWind] = useState(null);
  const [pois, setPois] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({ distance: 0, duration: 0 });
  
  // Settings
  const [settings, setSettings] = useState({
    cone_aperture: 60,
    cone_range: 500,
    auto_rotate_map: true,
    show_wind_indicator: true
  });
  
  // Loading states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Refs
  const watchIdRef = useRef(null);
  const updateIntervalRef = useRef(null);
  
  // Initialize session
  const initSession = useCallback(async (lat, lng, initialHeading = 0) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/live-heading/session/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          lat,
          lng,
          heading: initialHeading,
          cone_aperture: settings.cone_aperture,
          cone_range: settings.cone_range
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
        setSessionState('active');
        setLoading(false);
        return data.session_id;
      } else {
        throw new Error(data.message || 'Failed to create session');
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  }, [userId, settings.cone_aperture, settings.cone_range]);
  
  // Update position
  const updatePosition = useCallback(async (lat, lng, newHeading) => {
    if (!sessionId || sessionState !== 'active') return;
    
    try {
      const response = await fetch(`${API_URL}/api/v1/live-heading/session/${sessionId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          lat,
          lng,
          heading: newHeading
        })
      });
      
      const data = await response.json();
      
      setPosition({ lat, lng });
      setHeading(newHeading);
      setViewCone(data.view_cone);
      setWind(data.wind);
      setPois(data.pois || []);
      setAlerts(data.alerts || []);
      setStats({
        distance: data.distance_traveled_m,
        duration: data.duration_seconds
      });
    } catch (err) {
      console.error('Position update failed:', err);
    }
  }, [sessionId, sessionState]);
  
  // Handle geolocation
  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Géolocalisation non supportée');
      setLoading(false);
      return;
    }
    
    // Get initial position
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setPosition({ lat: latitude, lng: longitude });
        
        // Get initial heading from device orientation if available
        let initialHeading = 0;
        if (pos.coords.heading !== null) {
          initialHeading = pos.coords.heading;
        }
        setHeading(initialHeading);
        
        // Initialize session
        const sid = await initSession(latitude, longitude, initialHeading);
        
        if (sid) {
          // Start watching position
          watchIdRef.current = navigator.geolocation.watchPosition(
            (newPos) => {
              const newHeading = newPos.coords.heading || heading;
              updatePosition(newPos.coords.latitude, newPos.coords.longitude, newHeading);
            },
            (err) => console.error('Watch position error:', err),
            { enableHighAccuracy: true, maximumAge: 1000, timeout: 5000 }
          );
        }
      },
      (err) => {
        // Fallback to demo position (Quebec City)
        const demoLat = 46.8139;
        const demoLng = -71.2082;
        setPosition({ lat: demoLat, lng: demoLng });
        initSession(demoLat, demoLng, 45);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
    
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
      }
    };
  }, []);
  
  // Handle device orientation for heading
  useEffect(() => {
    const handleOrientation = (event) => {
      if (event.alpha !== null && sessionState === 'active') {
        // Convert alpha to compass heading (0 = North)
        let compassHeading = 360 - event.alpha;
        if (compassHeading < 0) compassHeading += 360;
        if (compassHeading >= 360) compassHeading -= 360;
        
        setHeading(Math.round(compassHeading));
      }
    };
    
    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', handleOrientation, true);
    }
    
    return () => {
      window.removeEventListener('deviceorientation', handleOrientation);
    };
  }, [sessionState]);
  
  // End session
  const handleEndSession = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`${API_URL}/api/v1/live-heading/session/${sessionId}/end`, {
        method: 'POST'
      });
      const data = await response.json();
      
      setSessionState('ended');
      
      if (onClose) {
        onClose(data.summary);
      }
    } catch (err) {
      console.error('End session failed:', err);
    }
  };
  
  // Pause/Resume session
  const handlePauseResume = async () => {
    if (!sessionId) return;
    
    const action = sessionState === 'active' ? 'pause' : 'resume';
    
    try {
      await fetch(`${API_URL}/api/v1/live-heading/session/${sessionId}/${action}`, {
        method: 'POST'
      });
      
      setSessionState(action === 'pause' ? 'paused' : 'active');
    } catch (err) {
      console.error(`${action} session failed:`, err);
    }
  };
  
  // Acknowledge alert
  const handleAcknowledgeAlert = async (alertId) => {
    if (!sessionId) return;
    
    try {
      await fetch(`${API_URL}/api/v1/live-heading/session/${sessionId}/alert/${alertId}/acknowledge`, {
        method: 'POST'
      });
      
      setAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (err) {
      console.error('Acknowledge alert failed:', err);
    }
  };
  
  // Render loading state
  if (loading) {
    return (
      <div className="fixed inset-0 bg-slate-900 flex items-center justify-center z-50">
        <div className="text-center text-white">
          <div className="animate-spin w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-lg">Initialisation du Live Heading View...</p>
          <p className="text-sm text-slate-400 mt-2">Acquisition de la position GPS</p>
        </div>
      </div>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <div className="fixed inset-0 bg-slate-900 flex items-center justify-center z-50">
        <Card className="p-6 bg-slate-800 text-white max-w-md">
          <h3 className="text-xl font-bold text-red-400 mb-4">Erreur</h3>
          <p className="mb-4">{error}</p>
          <Button onClick={onClose} variant="outline">Fermer</Button>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="fixed inset-0 bg-slate-900 z-50 overflow-hidden">
      {/* Main Map Area */}
      <div 
        className="absolute inset-0 bg-gradient-to-b from-slate-800 to-slate-900"
        style={{
          transform: settings.auto_rotate_map ? `rotate(${-heading}deg)` : 'none',
          transition: 'transform 0.3s ease-out'
        }}
      >
        {/* Simulated Map Grid */}
        <div className="absolute inset-0 opacity-20">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#64748b" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        
        {/* Forward Cone Visualization */}
        <div className="absolute inset-0 flex items-center justify-center">
          <svg 
            className="w-full h-full max-w-2xl max-h-2xl"
            viewBox="0 0 400 400"
            style={{ transform: settings.auto_rotate_map ? `rotate(${heading}deg)` : 'none' }}
          >
            {/* Cone */}
            <defs>
              <linearGradient id="coneGradient" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
              </linearGradient>
            </defs>
            <path
              d={`M 200 250 L ${200 - Math.tan(settings.cone_aperture/2 * Math.PI/180) * 180} 70 
                  A 180 180 0 0 1 ${200 + Math.tan(settings.cone_aperture/2 * Math.PI/180) * 180} 70 Z`}
              fill="url(#coneGradient)"
              stroke="#10b981"
              strokeWidth="2"
              strokeOpacity="0.6"
            />
            
            {/* Direction Line */}
            <line 
              x1="200" y1="250" 
              x2="200" y2="70" 
              stroke="#10b981" 
              strokeWidth="2" 
              strokeDasharray="8,4"
            />
            
            {/* Center Point (User Position) */}
            <circle cx="200" cy="250" r="8" fill="#10b981" />
            <circle cx="200" cy="250" r="12" fill="none" stroke="#10b981" strokeWidth="2" opacity="0.5" />
            <circle cx="200" cy="250" r="18" fill="none" stroke="#10b981" strokeWidth="1" opacity="0.3" />
          </svg>
        </div>
        
        {/* POI Markers */}
        {pois.map((poi, index) => (
          <POIMarker
            key={poi.id}
            poi={poi}
            index={index}
            heading={heading}
            autoRotate={settings.auto_rotate_map}
          />
        ))}
      </div>
      
      {/* Fixed UI Elements */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Bar - Stats */}
        <div className="absolute top-0 left-0 right-0 p-4 pointer-events-auto">
          <SessionStats 
            distance={stats.distance}
            duration={stats.duration}
            poisCount={pois.length}
            sessionState={sessionState}
          />
        </div>
        
        {/* Compass Widget */}
        <div className="absolute top-20 right-4 pointer-events-auto">
          <CompassWidget heading={heading} />
        </div>
        
        {/* Wind Indicator */}
        {settings.show_wind_indicator && wind && (
          <div className="absolute top-20 left-4 pointer-events-auto">
            <WindIndicator wind={wind} userHeading={heading} />
          </div>
        )}
        
        {/* Alerts */}
        <div className="absolute top-40 left-1/2 transform -translate-x-1/2 space-y-2 pointer-events-auto">
          {alerts.slice(0, 3).map(alert => (
            <AlertToast
              key={alert.id}
              alert={alert}
              onDismiss={() => handleAcknowledgeAlert(alert.id)}
            />
          ))}
        </div>
        
        {/* Bottom Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-4 pointer-events-auto">
          <SessionControls
            sessionState={sessionState}
            onPauseResume={handlePauseResume}
            onEnd={handleEndSession}
            onClose={onClose}
          />
        </div>
        
        {/* Position Info */}
        {position && (
          <div className="absolute bottom-24 left-4 text-xs text-slate-400 font-mono">
            {position.lat.toFixed(5)}, {position.lng.toFixed(5)}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveHeadingView;
