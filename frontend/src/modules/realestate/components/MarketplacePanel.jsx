/**
 * MarketplacePanel - Internal marketplace for properties
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Button } from '../../../components/ui/button';
import { 
  Store, Plus, Search, Heart, Clock 
} from 'lucide-react';

/**
 * Marketplace Panel Component
 * 
 * @param {Object} props
 * @param {Function} props.onCreateListing - Create listing callback
 */
const MarketplacePanel = ({ 
  onCreateListing = null
}) => {
  const [activeTab, setActiveTab] = useState('browse');

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[var(--bionic-text-primary)] flex items-center gap-2">
          <Store className="w-5 h-5 text-[var(--bionic-gold-primary)]" />
          Marketplace BIONIC
        </h3>
        <Button
          size="sm"
          onClick={onCreateListing}
          className="bg-[var(--bionic-gold-primary)] text-black hover:bg-[var(--bionic-gold-secondary)]"
        >
          <Plus className="w-4 h-4 mr-1" />
          Créer une annonce
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[var(--bionic-bg-hover)] w-full">
          <TabsTrigger 
            value="browse"
            className="data-[state=active]:text-[var(--bionic-gold-primary)]"
          >
            <Search className="w-4 h-4 mr-1" />
            Parcourir
          </TabsTrigger>
          <TabsTrigger 
            value="favorites"
            className="data-[state=active]:text-[var(--bionic-gold-primary)]"
          >
            <Heart className="w-4 h-4 mr-1" />
            Favoris
          </TabsTrigger>
          <TabsTrigger 
            value="my-listings"
            className="data-[state=active]:text-[var(--bionic-gold-primary)]"
          >
            <Clock className="w-4 h-4 mr-1" />
            Mes annonces
          </TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="mt-4">
          <div className="text-center py-12 text-[var(--bionic-text-muted)]">
            <Store className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">Marketplace en développement</p>
            <p className="text-xs mt-1">Bientôt disponible</p>
          </div>
        </TabsContent>

        <TabsContent value="favorites" className="mt-4">
          <div className="text-center py-12 text-[var(--bionic-text-muted)]">
            <Heart className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">Aucun favori</p>
            <p className="text-xs mt-1">Ajoutez des propriétés à vos favoris</p>
          </div>
        </TabsContent>

        <TabsContent value="my-listings" className="mt-4">
          <div className="text-center py-12 text-[var(--bionic-text-muted)]">
            <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">Aucune annonce</p>
            <p className="text-xs mt-1">Créez votre première annonce</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MarketplacePanel;
