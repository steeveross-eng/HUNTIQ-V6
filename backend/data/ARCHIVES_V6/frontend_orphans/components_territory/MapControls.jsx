/**
 * MapControls - GPS coordinates input and map scale controls
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MapPin, Navigation, Target, Crosshair } from 'lucide-react';
import { toast } from 'sonner';

// GPS Format conversion utilities
export const dmsToDecimal = (deg, min, sec, dir) => {
  const d = parseFloat(deg) || 0;
  const m = parseFloat(min) || 0;
  const s = parseFloat(sec) || 0;
  let decimal = d + (m / 60) + (s / 3600);
  if (dir === 'S' || dir === 'W') decimal *= -1;
  return decimal;
};

export const decimalToDms = (decimal, isLat) => {
  const dir = isLat ? (decimal >= 0 ? 'N' : 'S') : (decimal >= 0 ? 'E' : 'W');
  const abs = Math.abs(decimal);
  const deg = Math.floor(abs);
  const minFloat = (abs - deg) * 60;
  const min = Math.floor(minFloat);
  const sec = ((minFloat - min) * 60).toFixed(2);
  return { deg, min, sec, dir };
};

// Scale to zoom mapping
export const SCALE_TO_ZOOM = {
  '1:1000': 18,
  '1:5000': 16,
  '1:10000': 14,
  '1:25000': 13,
  '1:50000': 11,
  '1:100000': 10,
  '1:250000': 8,
};

const MapControls = ({ 
  onNavigate, 
  mapCenter, 
  mapZoom, 
  onZoomChange,
  mouseGpsPreview 
}) => {
  const [gpsFormat, setGpsFormat] = useState('decimal');
  const [gpsLatitude, setGpsLatitude] = useState('');
  const [gpsLongitude, setGpsLongitude] = useState('');
  const [mapScale, setMapScale] = useState('1:5000');
  
  // DMS fields
  const [dmsLatDeg, setDmsLatDeg] = useState('');
  const [dmsLatMin, setDmsLatMin] = useState('');
  const [dmsLatSec, setDmsLatSec] = useState('');
  const [dmsLatDir, setDmsLatDir] = useState('N');
  const [dmsLonDeg, setDmsLonDeg] = useState('');
  const [dmsLonMin, setDmsLonMin] = useState('');
  const [dmsLonSec, setDmsLonSec] = useState('');
  const [dmsLonDir, setDmsLonDir] = useState('W');

  const handleNavigate = () => {
    let lat, lon;
    
    if (gpsFormat === 'decimal') {
      lat = parseFloat(gpsLatitude);
      lon = parseFloat(gpsLongitude);
    } else {
      lat = dmsToDecimal(dmsLatDeg, dmsLatMin, dmsLatSec, dmsLatDir);
      lon = dmsToDecimal(dmsLonDeg, dmsLonMin, dmsLonSec, dmsLonDir);
    }
    
    if (isNaN(lat) || isNaN(lon)) {
      toast.error('Coordonnées invalides');
      return;
    }
    
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      toast.error('Coordonnées hors limites');
      return;
    }
    
    onNavigate([lat, lon]);
    toast.success(`Navigation vers ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
  };

  const handleScaleChange = (scale) => {
    setMapScale(scale);
    onZoomChange(SCALE_TO_ZOOM[scale]);
  };

  const handleMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          onNavigate([latitude, longitude]);
          toast.success('Position GPS trouvée');
        },
        (error) => {
          toast.error('Impossible d\'obtenir votre position');
        }
      );
    } else {
      toast.error('Géolocalisation non supportée');
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center gap-2">
          <Crosshair className="h-4 w-4 text-[#f5a623]" />
          Coordonnées GPS
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Format selector */}
        <div className="flex gap-2">
          <Button
            size="sm"
            variant={gpsFormat === 'decimal' ? 'default' : 'outline'}
            onClick={() => setGpsFormat('decimal')}
            className={gpsFormat === 'decimal' ? 'bg-[#f5a623] text-black' : ''}
          >
            Décimal
          </Button>
          <Button
            size="sm"
            variant={gpsFormat === 'dms' ? 'default' : 'outline'}
            onClick={() => setGpsFormat('dms')}
            className={gpsFormat === 'dms' ? 'bg-[#f5a623] text-black' : ''}
          >
            DMS
          </Button>
        </div>

        {/* Decimal format inputs */}
        {gpsFormat === 'decimal' && (
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-xs text-gray-400">Latitude</Label>
              <Input
                type="number"
                step="any"
                placeholder="46.8139"
                value={gpsLatitude}
                onChange={(e) => setGpsLatitude(e.target.value)}
                className="bg-background text-sm h-8"
              />
            </div>
            <div>
              <Label className="text-xs text-gray-400">Longitude</Label>
              <Input
                type="number"
                step="any"
                placeholder="-71.2080"
                value={gpsLongitude}
                onChange={(e) => setGpsLongitude(e.target.value)}
                className="bg-background text-sm h-8"
              />
            </div>
          </div>
        )}

        {/* DMS format inputs */}
        {gpsFormat === 'dms' && (
          <div className="space-y-2">
            <div className="flex items-center gap-1">
              <Input type="number" placeholder="46" value={dmsLatDeg} onChange={(e) => setDmsLatDeg(e.target.value)} className="w-12 bg-background text-xs h-7" />
              <span className="text-gray-400">°</span>
              <Input type="number" placeholder="48" value={dmsLatMin} onChange={(e) => setDmsLatMin(e.target.value)} className="w-12 bg-background text-xs h-7" />
              <span className="text-gray-400">'</span>
              <Input type="number" placeholder="50" value={dmsLatSec} onChange={(e) => setDmsLatSec(e.target.value)} className="w-14 bg-background text-xs h-7" />
              <span className="text-gray-400">"</span>
              <Select value={dmsLatDir} onValueChange={setDmsLatDir}>
                <SelectTrigger className="w-14 h-7 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="N">N</SelectItem>
                  <SelectItem value="S">S</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-1">
              <Input type="number" placeholder="71" value={dmsLonDeg} onChange={(e) => setDmsLonDeg(e.target.value)} className="w-12 bg-background text-xs h-7" />
              <span className="text-gray-400">°</span>
              <Input type="number" placeholder="12" value={dmsLonMin} onChange={(e) => setDmsLonMin(e.target.value)} className="w-12 bg-background text-xs h-7" />
              <span className="text-gray-400">'</span>
              <Input type="number" placeholder="29" value={dmsLonSec} onChange={(e) => setDmsLonSec(e.target.value)} className="w-14 bg-background text-xs h-7" />
              <span className="text-gray-400">"</span>
              <Select value={dmsLonDir} onValueChange={setDmsLonDir}>
                <SelectTrigger className="w-14 h-7 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="E">E</SelectItem>
                  <SelectItem value="W">W</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        {/* Navigate button */}
        <div className="flex gap-2">
          <Button 
            size="sm" 
            className="flex-1 bg-[#f5a623] hover:bg-[#d4891c] text-black"
            onClick={handleNavigate}
          >
            <Navigation className="h-4 w-4 mr-1" />
            Naviguer
          </Button>
          <Button 
            size="sm" 
            variant="outline"
            onClick={handleMyLocation}
            title="Ma position"
          >
            <Target className="h-4 w-4" />
          </Button>
        </div>

        {/* Scale selector */}
        <div>
          <Label className="text-xs text-gray-400">Échelle de carte</Label>
          <Select value={mapScale} onValueChange={handleScaleChange}>
            <SelectTrigger className="bg-background h-8 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(SCALE_TO_ZOOM).map((scale) => (
                <SelectItem key={scale} value={scale}>{scale}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Mouse GPS preview */}
        {mouseGpsPreview && (
          <div className="text-xs text-gray-400 bg-background rounded p-2">
            <MapPin className="h-3 w-3 inline mr-1 text-[#f5a623]" />
            {mouseGpsPreview.lat.toFixed(6)}, {mouseGpsPreview.lng.toFixed(6)}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MapControls;
