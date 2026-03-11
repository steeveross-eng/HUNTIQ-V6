/**
 * MarketingCalendarPage - Calendrier Marketing 60 Jours
 * =====================================================
 * 
 * Module Marketing Calendar V2 - BIONIC Premium
 * - Calendrier 60 jours à l'avance
 * - Génération de campagnes IA (GPT-5.2)
 * - Templates Premium + Animations Lottie
 * - Personnalisation par audience
 * - Prévisualisation multi-plateforme
 * 
 * Architecture LEGO V5 - Module isolé.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { 
  Calendar, Plus, RefreshCw, Eye, Send, 
  Users, Target, Sparkles, Clock, CheckCircle,
  ArrowLeft, ChevronLeft, ChevronRight, Filter,
  MessageSquare, Image, Hash, TrendingUp, Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Types d'audience
const AUDIENCE_TYPES = [
  { value: 'fabricants', label: 'Fabricants & Marques', icon: '🏭', color: 'bg-blue-500' },
  { value: 'affiliation', label: 'Programme Affiliation', icon: '🤝', color: 'bg-green-500' },
  { value: 'partenariats', label: 'Partenariats', icon: '🎯', color: 'bg-purple-500' },
  { value: 'prospects', label: 'Prospects', icon: '👥', color: 'bg-amber-500' },
  { value: 'audiences_specialisees', label: 'Audiences Spécialisées', icon: '🎿', color: 'bg-cyan-500' },
  { value: 'general', label: 'Audience Générale', icon: '🌐', color: 'bg-gray-500' }
];

// Tons de communication
const CONTENT_TONES = [
  { value: 'professional', label: 'Professionnel', emoji: '💼' },
  { value: 'premium', label: 'Premium', emoji: '✨' },
  { value: 'friendly', label: 'Amical', emoji: '🤝' },
  { value: 'urgent', label: 'Urgent', emoji: '⚡' },
  { value: 'exclusive', label: 'Exclusif', emoji: '🔒' },
  { value: 'educational', label: 'Éducatif', emoji: '📚' }
];

// Plateformes
const PLATFORMS = [
  { value: 'meta_feed', label: 'Meta Feed', icon: '📱' },
  { value: 'meta_story', label: 'Meta Story', icon: '📸' },
  { value: 'meta_carousel', label: 'Meta Carousel', icon: '🎠' },
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
  { value: 'youtube_thumbnail', label: 'YouTube', icon: '▶️' },
  { value: 'email_header', label: 'Email', icon: '📧' }
];

const MarketingCalendarPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('calendar');
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Form state for new campaign
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    scheduled_date: '',
    audience_type: 'prospects',
    tone: 'premium',
    platforms: ['meta_feed', 'meta_story'],
    product_focus: '',
    custom_keywords: []
  });
  
  // Preview state
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Load calendar
  const loadCalendar = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/marketing-calendar/calendar?days_ahead=60`);
      const data = await response.json();
      setCalendar(data);
    } catch (error) {
      console.error('Error loading calendar:', error);
      toast.error('Erreur lors du chargement du calendrier');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCalendar();
  }, [loadCalendar]);

  // Generate campaign
  const generateCampaign = async () => {
    if (!newCampaign.name || !newCampaign.scheduled_date) {
      toast.error('Veuillez remplir le nom et la date de la campagne');
      return;
    }
    
    setGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/marketing-calendar/campaigns/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newCampaign,
          scheduled_date: new Date(newCampaign.scheduled_date).toISOString()
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success(`Campagne générée en ${(data.generation_time_ms / 1000).toFixed(1)}s !`);
        setPreview(data.campaign);
        loadCalendar();
        setActiveTab('preview');
      } else {
        toast.error(data.error || 'Erreur lors de la génération');
      }
    } catch (error) {
      console.error('Error generating campaign:', error);
      toast.error('Erreur lors de la génération');
    } finally {
      setGenerating(false);
    }
  };

  // Quick preview
  const generatePreview = async () => {
    setPreviewLoading(true);
    try {
      const params = new URLSearchParams({
        audience_type: newCampaign.audience_type,
        tone: newCampaign.tone,
        platform: newCampaign.platforms[0] || 'meta_feed'
      });
      
      const response = await fetch(`${API_URL}/api/v1/marketing-calendar/preview?${params}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPreview({ content: data.preview });
        toast.success(`Prévisualisation générée en ${(data.generation_time_ms / 1000).toFixed(1)}s`);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      toast.error('Erreur lors de la prévisualisation');
    } finally {
      setPreviewLoading(false);
    }
  };

  // Calendar navigation
  const navigateMonth = (direction) => {
    const newDate = new Date(currentMonth);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentMonth(newDate);
  };

  // Get days for calendar grid
  const getCalendarDays = () => {
    if (!calendar) return [];
    
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPadding = firstDay.getDay();
    
    const days = [];
    
    // Padding days from previous month
    for (let i = 0; i < startPadding; i++) {
      days.push({ date: null, empty: true });
    }
    
    // Days of current month
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const calendarDay = calendar.days?.find(d => d.date === dateStr);
      
      days.push({
        date: dateStr,
        day,
        campaigns: calendarDay?.campaigns || [],
        events: calendarDay?.events || [],
        suggestions: calendarDay?.suggestions || [],
        isToday: dateStr === new Date().toISOString().split('T')[0]
      });
    }
    
    return days;
  };

  return (
    <div 
      className="fixed inset-0 bg-slate-900 flex flex-col overflow-hidden"
      style={{ paddingTop: '64px' }}
      data-testid="marketing-calendar-page"
    >
      {/* Header */}
      <div className="flex-shrink-0 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700/50 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/')} 
              className="text-gray-400 hover:text-white h-8 px-2"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="h-5 w-px bg-slate-700" />
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-[#f5a623]" />
              <div>
                <h1 className="text-sm font-bold text-white leading-tight">Marketing Calendar V2</h1>
                <p className="text-[10px] text-slate-400 leading-tight">
                  60 Jours • Génération IA GPT-5.2 • Templates Premium
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge className="bg-green-600 text-white text-xs">
              <Clock className="h-3 w-3 mr-1" />
              SLA &lt; 60s
            </Badge>
            <Button 
              size="sm" 
              onClick={loadCalendar}
              className="bg-slate-700 hover:bg-slate-600 h-8"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex-shrink-0 bg-slate-900/95 border-b border-slate-800 px-4 py-1">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-slate-800/50 h-8">
            <TabsTrigger value="calendar" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black h-7 text-xs px-3">
              <Calendar className="h-3 w-3 mr-1.5" />
              Calendrier
            </TabsTrigger>
            <TabsTrigger value="generate" className="data-[state=active]:bg-green-600 h-7 text-xs px-3">
              <Sparkles className="h-3 w-3 mr-1.5" />
              Générer
            </TabsTrigger>
            <TabsTrigger value="preview" className="data-[state=active]:bg-purple-600 h-7 text-xs px-3">
              <Eye className="h-3 w-3 mr-1.5" />
              Prévisualisation
            </TabsTrigger>
            <TabsTrigger value="campaigns" className="data-[state=active]:bg-blue-600 h-7 text-xs px-3">
              <Target className="h-3 w-3 mr-1.5" />
              Campagnes
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Calendar Tab */}
        {activeTab === 'calendar' && (
          <div className="max-w-6xl mx-auto">
            {/* Month Navigation */}
            <div className="flex items-center justify-between mb-4">
              <Button variant="ghost" size="sm" onClick={() => navigateMonth(-1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-xl font-bold text-white">
                {currentMonth.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
              </h2>
              <Button variant="ghost" size="sm" onClick={() => navigateMonth(1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {/* Day headers */}
              {['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'].map(day => (
                <div key={day} className="text-center text-xs text-gray-400 py-2 font-medium">
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {getCalendarDays().map((day, idx) => (
                <div
                  key={idx}
                  className={`
                    min-h-[80px] p-1 rounded-lg border transition-all cursor-pointer
                    ${day.empty ? 'bg-transparent border-transparent' : 'bg-slate-800/50 border-slate-700 hover:border-[#f5a623]/50'}
                    ${day.isToday ? 'ring-2 ring-[#f5a623] ring-offset-2 ring-offset-slate-900' : ''}
                    ${selectedDate === day.date ? 'border-[#f5a623]' : ''}
                  `}
                  onClick={() => !day.empty && setSelectedDate(day.date)}
                >
                  {!day.empty && (
                    <>
                      <div className="text-xs text-gray-400 mb-1">{day.day}</div>
                      
                      {/* Campaigns */}
                      {day.campaigns?.slice(0, 2).map((campaign, i) => (
                        <div 
                          key={i}
                          className="text-[10px] bg-[#f5a623]/20 text-[#f5a623] rounded px-1 py-0.5 mb-0.5 truncate"
                        >
                          {campaign.name}
                        </div>
                      ))}
                      
                      {/* Events */}
                      {day.events?.slice(0, 1).map((event, i) => (
                        <div key={i} className="text-[10px] text-green-400 truncate">
                          {event}
                        </div>
                      ))}
                    </>
                  )}
                </div>
              ))}
            </div>
            
            {/* Stats */}
            {calendar && (
              <div className="grid grid-cols-3 gap-4 mt-6">
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold text-white">{calendar.total_campaigns}</div>
                    <div className="text-sm text-gray-400">Campagnes totales</div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold text-green-400">{calendar.total_scheduled}</div>
                    <div className="text-sm text-gray-400">Planifiées</div>
                  </CardContent>
                </Card>
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="p-4">
                    <div className="text-3xl font-bold text-amber-400">{calendar.total_draft}</div>
                    <div className="text-sm text-gray-400">Brouillons</div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* Generate Tab */}
        {activeTab === 'generate' && (
          <div className="max-w-4xl mx-auto">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-[#f5a623]" />
                  Générer une Campagne
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Campaign name */}
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Nom de la campagne</label>
                  <Input
                    value={newCampaign.name}
                    onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
                    placeholder="Ex: Lancement Printemps 2026"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
                
                {/* Date */}
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Date de diffusion</label>
                  <Input
                    type="datetime-local"
                    value={newCampaign.scheduled_date}
                    onChange={(e) => setNewCampaign({...newCampaign, scheduled_date: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
                
                {/* Audience */}
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Type d'audience</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {AUDIENCE_TYPES.map(audience => (
                      <button
                        key={audience.value}
                        onClick={() => setNewCampaign({...newCampaign, audience_type: audience.value})}
                        className={`
                          p-3 rounded-lg border text-left transition-all
                          ${newCampaign.audience_type === audience.value 
                            ? 'border-[#f5a623] bg-[#f5a623]/10' 
                            : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'}
                        `}
                      >
                        <div className="text-lg">{audience.icon}</div>
                        <div className="text-xs text-white font-medium">{audience.label}</div>
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Tone */}
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Ton de communication</label>
                  <Select 
                    value={newCampaign.tone}
                    onValueChange={(value) => setNewCampaign({...newCampaign, tone: value})}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CONTENT_TONES.map(tone => (
                        <SelectItem key={tone.value} value={tone.value}>
                          {tone.emoji} {tone.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Product focus */}
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Focus produit (optionnel)</label>
                  <Textarea
                    value={newCampaign.product_focus}
                    onChange={(e) => setNewCampaign({...newCampaign, product_focus: e.target.value})}
                    placeholder="Ex: Fonctionnalité BIONIC WQS, Scoring de waypoints..."
                    className="bg-slate-700 border-slate-600 text-white"
                    rows={2}
                  />
                </div>
                
                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={generatePreview}
                    disabled={previewLoading}
                    variant="outline"
                    className="flex-1"
                  >
                    <Eye className={`h-4 w-4 mr-2 ${previewLoading ? 'animate-pulse' : ''}`} />
                    Prévisualiser
                  </Button>
                  <Button
                    onClick={generateCampaign}
                    disabled={generating}
                    className="flex-1 bg-[#f5a623] hover:bg-[#d4891c] text-black"
                  >
                    <Sparkles className={`h-4 w-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                    {generating ? 'Génération...' : 'Générer la Campagne'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Preview Tab */}
        {activeTab === 'preview' && preview && (
          <div className="max-w-4xl mx-auto">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Eye className="h-5 w-5 text-purple-400" />
                  Prévisualisation de Campagne
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Content preview */}
                <div className="space-y-4">
                  {/* Meta Feed Preview */}
                  <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-10 h-10 rounded-full bg-[#f5a623] flex items-center justify-center font-bold text-black">
                        H
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white">BIONIC HUNT/Chasse</div>
                        <div className="text-xs text-gray-400">Sponsorisé</div>
                      </div>
                    </div>
                    
                    {/* Visual placeholder */}
                    <div className="aspect-video bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg mb-3 flex items-center justify-center border border-slate-700">
                      <div className="text-center">
                        <Image className="h-12 w-12 text-slate-600 mx-auto mb-2" />
                        <p className="text-sm text-slate-500">Visuel généré</p>
                      </div>
                    </div>
                    
                    {/* Content */}
                    <div className="space-y-2">
                      <h3 className="text-lg font-bold text-[#f5a623]">
                        {preview.content?.headline}
                      </h3>
                      {preview.content?.subheadline && (
                        <p className="text-sm text-gray-300">
                          {preview.content.subheadline}
                        </p>
                      )}
                      {preview.content?.body_text && (
                        <p className="text-sm text-gray-400">
                          {preview.content.body_text}
                        </p>
                      )}
                      
                      {/* Hashtags */}
                      {preview.content?.hashtags && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {preview.content.hashtags.map((tag, i) => (
                            <Badge key={i} variant="outline" className="text-xs text-blue-400 border-blue-400/30">
                              #{tag.replace('#', '')}
                            </Badge>
                          ))}
                        </div>
                      )}
                      
                      {/* CTA Button */}
                      <Button className="w-full mt-3 bg-[#f5a623] hover:bg-[#d4891c] text-black">
                        {preview.content?.cta_text || 'En savoir plus'}
                      </Button>
                    </div>
                  </div>
                  
                  {/* Metrics preview */}
                  {preview.previews?.[0]?.mock_engagement && (
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <TrendingUp className="h-5 w-5 text-green-400 mx-auto mb-1" />
                        <div className="text-lg font-bold text-white">
                          {preview.previews[0].mock_engagement.estimated_reach?.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400">Portée estimée</div>
                      </div>
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <Zap className="h-5 w-5 text-amber-400 mx-auto mb-1" />
                        <div className="text-lg font-bold text-white">
                          {preview.previews[0].mock_engagement.estimated_clicks?.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400">Clics estimés</div>
                      </div>
                      <div className="bg-slate-900 rounded-lg p-3 text-center">
                        <CheckCircle className="h-5 w-5 text-purple-400 mx-auto mb-1" />
                        <div className="text-lg font-bold text-white">
                          {preview.previews[0].mock_engagement.estimated_conversions?.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400">Conversions</div>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Campaigns Tab */}
        {activeTab === 'campaigns' && (
          <div className="max-w-4xl mx-auto">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-blue-400" />
                    Campagnes
                  </span>
                  <Badge className="bg-slate-700">{calendar?.total_campaigns || 0}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calendar?.days?.filter(d => d.campaigns?.length > 0).slice(0, 10).map((day, idx) => (
                  <div key={idx} className="mb-4">
                    {day.campaigns.map((campaign, i) => (
                      <div 
                        key={i}
                        className="bg-slate-900 rounded-lg p-4 border border-slate-700 hover:border-[#f5a623]/50 transition-all"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-white">{campaign.name}</h4>
                          <Badge 
                            className={
                              campaign.status === 'scheduled' ? 'bg-green-600' :
                              campaign.status === 'draft' ? 'bg-amber-600' : 'bg-gray-600'
                            }
                          >
                            {campaign.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-400">
                          📅 {new Date(campaign.scheduled_date).toLocaleDateString('fr-FR')}
                          {' • '}
                          🎯 {AUDIENCE_TYPES.find(a => a.value === campaign.audience_type)?.label || campaign.audience_type}
                        </div>
                        {campaign.content?.headline && (
                          <p className="text-sm text-[#f5a623] mt-2 font-medium">
                            "{campaign.content.headline}"
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
                
                {(!calendar?.total_campaigns || calendar.total_campaigns === 0) && (
                  <div className="text-center py-8 text-gray-400">
                    <Calendar className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>Aucune campagne planifiée</p>
                    <Button 
                      onClick={() => setActiveTab('generate')}
                      className="mt-3 bg-[#f5a623] hover:bg-[#d4891c] text-black"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Créer une campagne
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketingCalendarPage;
