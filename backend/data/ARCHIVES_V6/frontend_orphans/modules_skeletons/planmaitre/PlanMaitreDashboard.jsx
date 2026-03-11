/**
 * PlanMaitreDashboard - Central dashboard for Plan Maître modules
 * Phase 10 - Plan Maître Integration
 * Updated: Phase 8 - Added Legal Time Engine integration
 * Version: 1.1.0 - BIONIC Design System Compliance
 */
import React, { useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { useLanguage } from '../../contexts/LanguageContext';
import { 
  Rocket, BarChart3, Clock, Sparkles, CircleDot, Map, Users,
  MapPin, FileText, AlertTriangle, Calendar, Eye, Edit, Megaphone
} from 'lucide-react';

// Plan Maître Module Imports
import { RecommendationPanel } from '../recommendation';
import { WildlifeTracker, SpeciesSelector } from '../wildlife';
import { TerritoryList, WaypointManager } from '../territory';
import { PredictiveWidget } from '../predictive';
import { SightingsFeed } from '../collaborative';
import { HabitatAnalysis } from '../ecoforestry';
import { ActivityChart } from '../behavioral';
import { LegalTimeWidget, LegalTimeBar } from '../legaltime';

const DEFAULT_COORDS = { lat: 46.8139, lng: -71.2082 }; // Quebec City

export const PlanMaitreDashboard = ({ 
  coordinates = DEFAULT_COORDS
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSpecies, setSelectedSpecies] = useState('deer');
  const [selectedSeason, setSelectedSeason] = useState('rut');

  const handleSpeciesChange = useCallback((species) => {
    setSelectedSpecies(species);
  }, []);

  return (
    <div className="space-y-6" data-testid="plan-maitre-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--bionic-text-primary)] flex items-center gap-3">
            <Rocket className="h-7 w-7 text-[var(--bionic-gold-primary)]" />
            {t('plan_maitre_title') || 'Plan Maître BIONIC™'}
          </h1>
          <p className="text-[var(--bionic-text-secondary)] text-sm mt-1">
            {t('plan_maitre_subtitle') || 'Modules Avancés'} • Phase 10
          </p>
        </div>
        
        {/* Module Status */}
        <div className="flex items-center gap-2">
          <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">legal-time</Badge>
          <Badge className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-light)]">recommendation</Badge>
          <Badge className="bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)]">wildlife</Badge>
          <Badge className="bg-[var(--bionic-blue-muted)] text-[var(--bionic-blue-light)]">predictive</Badge>
          <Badge className="bg-[var(--bionic-purple-muted)] text-[var(--bionic-purple-primary)]">collaborative</Badge>
        </div>
      </div>

      {/* Species Selector */}
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <CardContent className="p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <span className="text-[var(--bionic-text-secondary)] text-sm">{t('common_target_species') || 'Espèce cible'}:</span>
            <SpeciesSelector 
              selected={selectedSpecies}
              onSelect={handleSpeciesChange}
              showCategories={false}
            />
          </div>
        </CardContent>
      </Card>

      {/* Legal Time Status Bar */}
      <LegalTimeBar coordinates={coordinates} />

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-secondary)] w-full justify-start flex-wrap">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <BarChart3 className="h-4 w-4" /> {t('common_overview') || "Vue d'ensemble"}
          </TabsTrigger>
          <TabsTrigger value="legal-times" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Clock className="h-4 w-4" /> {t('legal_times') || 'Heures Légales'}
          </TabsTrigger>
          <TabsTrigger value="prediction" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Sparkles className="h-4 w-4" /> {t('common_prediction') || 'Prédiction'}
          </TabsTrigger>
          <TabsTrigger value="wildlife" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <CircleDot className="h-4 w-4" /> {t('common_wildlife') || 'Faune'}
          </TabsTrigger>
          <TabsTrigger value="territory" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Map className="h-4 w-4" /> {t('common_territory') || 'Territoire'}
          </TabsTrigger>
          <TabsTrigger value="community" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Users className="h-4 w-4" /> {t('common_community') || 'Communauté'}
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              <LegalTimeWidget 
                coordinates={coordinates}
                compact={true}
              />
              <RecommendationPanel 
                species={selectedSpecies}
                season={selectedSeason}
              />
            </div>

            {/* Center Column */}
            <div className="space-y-4">
              <PredictiveWidget 
                species={selectedSpecies}
                coordinates={coordinates}
                compact={false}
              />
              
              <ActivityChart 
                species={selectedSpecies}
              />
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <WildlifeTracker 
                species={selectedSpecies}
                coordinates={coordinates}
              />
              
              <SightingsFeed 
                coordinates={coordinates}
                radiusKm={15}
              />
            </div>
          </div>
        </TabsContent>

        {/* Legal Times Tab - NEW */}
        <TabsContent value="legal-times" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LegalTimeWidget 
              coordinates={coordinates}
              showSlots={true}
            />
            
            <div className="space-y-4">
              <Card className="bg-gradient-to-br from-[var(--bionic-blue-muted)] to-[var(--bionic-bg-card)] border-[var(--bionic-blue-light)]/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-[var(--bionic-blue-light)]" />
                    {t('legal_position_calc') || 'Position de calcul'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3">
                        <p className="text-[var(--bionic-text-muted)] text-xs">{t('common_latitude') || 'Latitude'}</p>
                        <p className="text-[var(--bionic-text-primary)] font-medium">{coordinates.lat.toFixed(4)}</p>
                      </div>
                      <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3">
                        <p className="text-[var(--bionic-text-muted)] text-xs">{t('common_longitude') || 'Longitude'}</p>
                        <p className="text-[var(--bionic-text-primary)] font-medium">{coordinates.lng.toFixed(4)}</p>
                      </div>
                    </div>
                    <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3">
                      <p className="text-[var(--bionic-text-muted)] text-xs mb-1">{t('common_region') || 'Région'}</p>
                      <p className="text-[var(--bionic-text-primary)] font-medium">Québec, QC, Canada</p>
                    </div>
                    <div className="bg-[var(--bionic-gold-muted)] border border-[var(--bionic-gold-primary)]/50 rounded-lg p-3">
                      <p className="text-[var(--bionic-gold-primary)] text-sm flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4" />
                        {t('legal_times_vary') || 'Les heures légales varient selon votre position exacte'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-[var(--bionic-purple-muted)] to-[var(--bionic-bg-card)] border-[var(--bionic-purple-primary)]/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <FileText className="h-5 w-5 text-[var(--bionic-purple-primary)]" />
                    {t('legal_regulations') || 'Règlementation'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3">
                      <p className="text-[var(--bionic-purple-primary)] font-medium mb-1">{t('legal_period') || 'Période de chasse légale'}</p>
                      <p className="text-[var(--bionic-text-secondary)]">
                        {t('legal_period_desc') || '30 minutes avant le lever du soleil jusqu\'à 30 minutes après le coucher du soleil'}
                      </p>
                    </div>
                    <div className="bg-[var(--bionic-bg-secondary)] rounded-lg p-3">
                      <p className="text-[var(--bionic-purple-primary)] font-medium mb-1">{t('common_source') || 'Source'}</p>
                      <p className="text-[var(--bionic-text-secondary)]">
                        {t('legal_source_mffp') || 'Règlement sur la chasse du Québec - MFFP'}
                      </p>
                    </div>
                    <div className="bg-[var(--bionic-red-muted)] border border-[var(--bionic-red-primary)]/50 rounded-lg p-3">
                      <p className="text-[var(--bionic-red-primary)] text-xs flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4" />
                        {t('legal_warning') || 'La chasse en dehors des heures légales est une infraction grave'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Prediction Tab */}
        <TabsContent value="prediction" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <PredictiveWidget 
                species={selectedSpecies}
                coordinates={coordinates}
              />
            </div>

            <div className="space-y-4">
              <LegalTimeWidget 
                coordinates={coordinates}
                showSlots={true}
              />
              
              <ActivityChart 
                species={selectedSpecies}
              />
            </div>
          </div>
        </TabsContent>

        {/* Wildlife Tab */}
        <TabsContent value="wildlife" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <WildlifeTracker 
                species={selectedSpecies}
                coordinates={coordinates}
              />
              
              <ActivityChart 
                species={selectedSpecies}
              />
            </div>

            <div className="space-y-4">
              <HabitatAnalysis 
                coordinates={coordinates}
                species={selectedSpecies}
              />
              
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                    {t('wildlife_seasonal_behavior') || 'Comportement Saisonnier'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {['Pré-rut', 'Rut', 'Post-rut', 'Hiver'].map((season, i) => (
                      <button
                        key={season}
                        onClick={() => setSelectedSeason(season.toLowerCase().replace('-', '_'))}
                        className={`p-3 rounded-lg text-center transition-all ${
                          selectedSeason === season.toLowerCase().replace('-', '_')
                            ? 'bg-[var(--bionic-gold-primary)] text-black'
                            : 'bg-[var(--bionic-bg-secondary)] text-[var(--bionic-text-secondary)] hover:bg-[var(--bionic-bg-tertiary)]'
                        }`}
                      >
                        <div className="font-medium">{season}</div>
                        <div className="text-xs opacity-75">
                          {['Sept-Oct', 'Nov', 'Déc', 'Jan-Mar'][i]}
                        </div>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Territory Tab */}
        <TabsContent value="territory" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Waypoint Manager - Principal */}
              <WaypointManager coordinates={coordinates} />
              
              <TerritoryList showFilters={true} />
            </div>

            <div className="space-y-4">
              <HabitatAnalysis 
                coordinates={coordinates}
                species={selectedSpecies}
              />
              
              <Card className="bg-gradient-to-br from-[var(--bionic-blue-muted)] to-[var(--bionic-bg-card)] border-[var(--bionic-blue-light)]/50">
                <CardContent className="p-4">
                  <h4 className="text-[var(--bionic-text-primary)] font-medium mb-3 flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-[var(--bionic-blue-light)]" />
                    {t('common_current_position') || 'Position actuelle'}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-[var(--bionic-text-secondary)]">{t('common_latitude') || 'Latitude'}</span>
                      <span className="text-[var(--bionic-text-primary)]">{coordinates.lat.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--bionic-text-secondary)]">{t('common_longitude') || 'Longitude'}</span>
                      <span className="text-[var(--bionic-text-primary)]">{coordinates.lng.toFixed(4)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Community Tab */}
        <TabsContent value="community" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SightingsFeed 
              coordinates={coordinates}
              radiusKm={25}
              limit={15}
            />

            <div className="space-y-4">
              <RecommendationPanel 
                species={selectedSpecies}
                season={selectedSeason}
              />
              
              <Card className="bg-gradient-to-br from-[var(--bionic-green-muted)] to-[var(--bionic-bg-card)] border-[var(--bionic-green-primary)]/50">
                <CardContent className="p-4">
                  <h4 className="text-[var(--bionic-green-primary)] font-medium mb-3 flex items-center gap-2">
                    <Megaphone className="h-5 w-5" />
                    {t('community_contribute') || 'Contribuer'}
                  </h4>
                  <div className="space-y-2">
                    <Button className="w-full bg-[var(--bionic-green-primary)] hover:bg-[var(--bionic-green-light)]">
                      <Eye className="h-4 w-4 mr-2" /> {t('community_report_sighting') || 'Signaler une observation'}
                    </Button>
                    <Button variant="outline" className="w-full border-[var(--bionic-green-primary)] text-[var(--bionic-green-primary)]">
                      <Edit className="h-4 w-4 mr-2" /> {t('community_submit_report') || 'Soumettre un rapport'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PlanMaitreDashboard;
