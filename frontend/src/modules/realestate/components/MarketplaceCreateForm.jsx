/**
 * MarketplaceCreateForm - Form to create marketplace listing
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { 
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue 
} from '../../../components/ui/select';
import { 
  Plus, Upload, MapPin, DollarSign, Ruler, Save, X 
} from 'lucide-react';

/**
 * Marketplace Create Form Component
 * 
 * @param {Object} props
 * @param {Function} props.onSubmit - Form submit callback
 * @param {Function} props.onCancel - Cancel callback
 */
const MarketplaceCreateForm = ({ 
  onSubmit = null,
  onCancel = null
}) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    area_m2: '',
    property_type: 'terrain',
    lat: '',
    lng: '',
    images: []
  });

  const handleChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(formData);
  };

  return (
    <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-primary)]">
      <CardHeader>
        <CardTitle className="text-[var(--bionic-text-primary)] flex items-center gap-2">
          <Plus className="w-5 h-5 text-[var(--bionic-gold-primary)]" />
          Nouvelle Annonce
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-muted)]">Titre de l'annonce</Label>
            <Input
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="Ex: Terrain boisé 50 hectares"
              className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]"
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-muted)]">Description</Label>
            <Textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Décrivez la propriété..."
              className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)] min-h-[100px]"
            />
          </div>

          {/* Price & Area */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-[var(--bionic-text-muted)] flex items-center gap-1">
                <DollarSign className="w-3 h-3" /> Prix
              </Label>
              <Input
                type="number"
                value={formData.price}
                onChange={(e) => handleChange('price', e.target.value)}
                placeholder="150000"
                className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]"
                required
              />
            </div>
            <div className="space-y-2">
              <Label className="text-[var(--bionic-text-muted)] flex items-center gap-1">
                <Ruler className="w-3 h-3" /> Superficie (m²)
              </Label>
              <Input
                type="number"
                value={formData.area_m2}
                onChange={(e) => handleChange('area_m2', e.target.value)}
                placeholder="500000"
                className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]"
                required
              />
            </div>
          </div>

          {/* Property Type */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-muted)]">Type de propriété</Label>
            <Select 
              value={formData.property_type} 
              onValueChange={(v) => handleChange('property_type', v)}
            >
              <SelectTrigger className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="terrain">Terrain</SelectItem>
                <SelectItem value="chalet">Chalet</SelectItem>
                <SelectItem value="ferme">Ferme</SelectItem>
                <SelectItem value="lot_boise">Lot boisé</SelectItem>
                <SelectItem value="pourvoirie">Pourvoirie</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Coordinates */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-[var(--bionic-text-muted)] flex items-center gap-1">
                <MapPin className="w-3 h-3" /> Latitude
              </Label>
              <Input
                type="number"
                step="any"
                value={formData.lat}
                onChange={(e) => handleChange('lat', e.target.value)}
                placeholder="46.8139"
                className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-[var(--bionic-text-muted)]">Longitude</Label>
              <Input
                type="number"
                step="any"
                value={formData.lng}
                onChange={(e) => handleChange('lng', e.target.value)}
                placeholder="-71.2080"
                className="bg-[var(--bionic-bg-hover)] border-[var(--bionic-border-secondary)]"
              />
            </div>
          </div>

          {/* Images Upload */}
          <div className="space-y-2">
            <Label className="text-[var(--bionic-text-muted)]">Images</Label>
            <div className="border-2 border-dashed border-[var(--bionic-border-secondary)] rounded-lg p-6 text-center">
              <Upload className="w-8 h-8 mx-auto text-[var(--bionic-text-muted)] mb-2" />
              <p className="text-sm text-[var(--bionic-text-muted)]">
                Glissez des images ou cliquez pour télécharger
              </p>
              <p className="text-xs text-[var(--bionic-text-muted)] mt-1">
                PNG, JPG jusqu'à 5MB
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-[var(--bionic-border-secondary)]">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              className="border-[var(--bionic-border-secondary)]"
            >
              <X className="w-4 h-4 mr-1" />
              Annuler
            </Button>
            <Button
              type="submit"
              className="bg-[var(--bionic-gold-primary)] text-black hover:bg-[var(--bionic-gold-secondary)]"
            >
              <Save className="w-4 h-4 mr-1" />
              Publier
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default MarketplaceCreateForm;
