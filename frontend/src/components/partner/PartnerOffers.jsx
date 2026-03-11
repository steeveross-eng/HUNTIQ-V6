/**
 * PartnerOffers - Manage partner offers/services
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Package,
  Plus,
  Edit,
  Trash2,
  Eye,
  DollarSign,
  MapPin,
  Users,
  Calendar,
  Star,
  ToggleLeft,
  ToggleRight,
  RefreshCw,
  Save
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Offer types
const OFFER_TYPES = {
  forfait: { fr: 'Forfait chasse', en: 'Hunting Package', icon: '🎯' },
  territoire: { fr: 'Territoire', en: 'Territory', icon: '🌲' },
  hebergement: { fr: 'Hébergement', en: 'Accommodation', icon: '🏠' },
  service: { fr: 'Service guidé', en: 'Guided Service', icon: '🧭' },
  equipement: { fr: 'Équipement', en: 'Equipment', icon: '🎒' },
  acces: { fr: 'Accès journalier', en: 'Day Access', icon: '🎫' }
};

const SPECIES_OPTIONS = [
  { value: 'orignal', label: { fr: 'Orignal', en: 'Moose' }, icon: '🫎' },
  { value: 'chevreuil', label: { fr: 'Chevreuil', en: 'Deer' }, icon: '🦌' },
  { value: 'ours', label: { fr: 'Ours', en: 'Bear' }, icon: '🐻' },
  { value: 'dindon', label: { fr: 'Dindon', en: 'Turkey' }, icon: '🦃' },
  { value: 'petit_gibier', label: { fr: 'Petit gibier', en: 'Small Game' }, icon: '🐰' },
  { value: 'sauvagine', label: { fr: 'Sauvagine', en: 'Waterfowl' }, icon: '🦆' }
];

const PartnerOffers = ({ partnerId, onOffersChange }) => {
  const { language } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [offers, setOffers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingOffer, setEditingOffer] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    offer_type: '',
    price: '',
    price_unit: 'jour',
    max_guests: '',
    location: '',
    species: [],
    rules: '',
    is_active: true
  });

  useEffect(() => {
    if (partnerId) {
      loadOffers();
    }
  }, [partnerId]);

  const loadOffers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/api/partnership/offers`, {
        params: { partner_id: partnerId }
      });
      setOffers(response.data);
      if (onOffersChange) onOffersChange(response.data);
    } catch (error) {
      console.error('Error loading offers:', error);
    }
    setLoading(false);
  };

  const openNewOfferModal = () => {
    setEditingOffer(null);
    setFormData({
      title: '',
      description: '',
      offer_type: '',
      price: '',
      price_unit: 'jour',
      max_guests: '',
      location: '',
      species: [],
      rules: '',
      is_active: true
    });
    setShowModal(true);
  };

  const openEditModal = (offer) => {
    setEditingOffer(offer);
    setFormData({
      title: offer.title,
      description: offer.description,
      offer_type: offer.offer_type,
      price: offer.price.toString(),
      price_unit: offer.price_unit,
      max_guests: offer.max_guests?.toString() || '',
      location: offer.location || '',
      species: offer.species || [],
      rules: offer.rules || '',
      is_active: offer.is_active
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.description || !formData.offer_type || !formData.price) {
      toast.error(language === 'fr' ? 'Veuillez remplir tous les champs obligatoires' : 'Please fill all required fields');
      return;
    }

    try {
      const data = {
        ...formData,
        price: parseFloat(formData.price),
        max_guests: formData.max_guests ? parseInt(formData.max_guests) : null
      };

      if (editingOffer) {
        await axios.put(`${API}/api/partnership/offers/${editingOffer.id}`, data);
        toast.success(language === 'fr' ? 'Offre mise à jour!' : 'Offer updated!');
      } else {
        await axios.post(`${API}/api/partnership/offers?partner_id=${partnerId}`, data);
        toast.success(language === 'fr' ? 'Offre créée!' : 'Offer created!');
      }

      setShowModal(false);
      loadOffers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error');
    }
  };

  const toggleOfferStatus = async (offer) => {
    try {
      await axios.put(`${API}/api/partnership/offers/${offer.id}`, {
        is_active: !offer.is_active
      });
      toast.success(offer.is_active 
        ? (language === 'fr' ? 'Offre désactivée' : 'Offer deactivated')
        : (language === 'fr' ? 'Offre activée' : 'Offer activated'));
      loadOffers();
    } catch (error) {
      toast.error('Error');
    }
  };

  const handleSpeciesToggle = (speciesValue) => {
    setFormData(prev => ({
      ...prev,
      species: prev.species.includes(speciesValue)
        ? prev.species.filter(s => s !== speciesValue)
        : [...prev.species, speciesValue]
    }));
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">
            {language === 'fr' ? 'Mes offres' : 'My Offers'}
          </h3>
          <p className="text-sm text-gray-400">
            {language === 'fr' 
              ? `${offers.length} offre(s) créée(s)`
              : `${offers.length} offer(s) created`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadOffers} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          <Button className="btn-golden text-black" onClick={openNewOfferModal}>
            <Plus className="h-4 w-4 mr-2" />
            {language === 'fr' ? 'Nouvelle offre' : 'New Offer'}
          </Button>
        </div>
      </div>

      {/* Offers Grid */}
      {offers.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="py-12 text-center">
            <Package className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <h4 className="text-white font-medium mb-2">
              {language === 'fr' ? 'Aucune offre pour le moment' : 'No offers yet'}
            </h4>
            <p className="text-gray-400 text-sm mb-4">
              {language === 'fr' 
                ? 'Créez votre première offre pour commencer à recevoir des réservations'
                : 'Create your first offer to start receiving bookings'}
            </p>
            <Button className="btn-golden text-black" onClick={openNewOfferModal}>
              <Plus className="h-4 w-4 mr-2" />
              {language === 'fr' ? 'Créer une offre' : 'Create Offer'}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {offers.map((offer) => (
            <Card key={offer.id} className={`bg-card border-border ${!offer.is_active ? 'opacity-60' : ''}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{OFFER_TYPES[offer.offer_type]?.icon || '📦'}</span>
                    <div>
                      <h4 className="font-semibold text-white">{offer.title}</h4>
                      <p className="text-xs text-gray-400">
                        {OFFER_TYPES[offer.offer_type]?.[language] || offer.offer_type}
                      </p>
                    </div>
                  </div>
                  <Badge className={offer.is_active ? 'bg-green-500/20 text-green-500' : 'bg-gray-500/20 text-gray-500'}>
                    {offer.is_active 
                      ? (language === 'fr' ? 'Actif' : 'Active')
                      : (language === 'fr' ? 'Inactif' : 'Inactive')}
                  </Badge>
                </div>

                <p className="text-sm text-gray-400 line-clamp-2 mb-3">{offer.description}</p>

                <div className="flex flex-wrap gap-2 mb-3">
                  <Badge variant="outline" className="text-[#f5a623] border-[#f5a623]">
                    <DollarSign className="h-3 w-3 mr-1" />
                    ${offer.price}/{offer.price_unit}
                  </Badge>
                  {offer.max_guests && (
                    <Badge variant="outline" className="text-blue-400 border-blue-400">
                      <Users className="h-3 w-3 mr-1" />
                      {offer.max_guests} max
                    </Badge>
                  )}
                  {offer.location && (
                    <Badge variant="outline" className="text-green-400 border-green-400">
                      <MapPin className="h-3 w-3 mr-1" />
                      {offer.location}
                    </Badge>
                  )}
                </div>

                {/* Species */}
                {offer.species?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {offer.species.map((sp) => {
                      const species = SPECIES_OPTIONS.find(s => s.value === sp);
                      return species ? (
                        <span key={sp} className="text-xs bg-background px-2 py-1 rounded">
                          {species.icon} {species.label[language]}
                        </span>
                      ) : null;
                    })}
                  </div>
                )}

                {/* Stats */}
                <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                  <span><Eye className="h-3 w-3 inline mr-1" />{offer.views || 0}</span>
                  <span><Calendar className="h-3 w-3 inline mr-1" />{offer.reservations_count || 0}</span>
                  {offer.rating > 0 && (
                    <span><Star className="h-3 w-3 inline mr-1 text-yellow-500" />{offer.rating.toFixed(1)}</span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => openEditModal(offer)}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    {language === 'fr' ? 'Modifier' : 'Edit'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => toggleOfferStatus(offer)}
                    className={offer.is_active ? 'text-gray-400' : 'text-green-400'}
                  >
                    {offer.is_active ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="bg-card border-border text-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Package className="h-5 w-5 text-[#f5a623]" />
              {editingOffer 
                ? (language === 'fr' ? 'Modifier l\'offre' : 'Edit Offer')
                : (language === 'fr' ? 'Nouvelle offre' : 'New Offer')}
            </DialogTitle>
            <DialogDescription>
              {language === 'fr' 
                ? 'Remplissez les informations de votre offre'
                : 'Fill in your offer information'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label>{language === 'fr' ? 'Titre *' : 'Title *'}</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder={language === 'fr' ? 'Forfait chasse à l\'orignal 7 jours' : 'Moose hunting package 7 days'}
                  className="bg-background"
                />
              </div>

              <div>
                <Label>{language === 'fr' ? 'Type d\'offre *' : 'Offer Type *'}</Label>
                <Select 
                  value={formData.offer_type} 
                  onValueChange={(v) => setFormData({ ...formData, offer_type: v })}
                >
                  <SelectTrigger className="bg-background">
                    <SelectValue placeholder={language === 'fr' ? 'Sélectionnez' : 'Select'} />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(OFFER_TYPES).map(([key, value]) => (
                      <SelectItem key={key} value={key}>
                        {value.icon} {value[language]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>{language === 'fr' ? 'Capacité max' : 'Max Guests'}</Label>
                <Input
                  type="number"
                  value={formData.max_guests}
                  onChange={(e) => setFormData({ ...formData, max_guests: e.target.value })}
                  placeholder="4"
                  className="bg-background"
                />
              </div>

              <div>
                <Label>{language === 'fr' ? 'Prix *' : 'Price *'}</Label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    placeholder="500"
                    className="bg-background"
                  />
                  <Select 
                    value={formData.price_unit} 
                    onValueChange={(v) => setFormData({ ...formData, price_unit: v })}
                  >
                    <SelectTrigger className="w-[120px] bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="jour">{language === 'fr' ? '/jour' : '/day'}</SelectItem>
                      <SelectItem value="nuit">{language === 'fr' ? '/nuit' : '/night'}</SelectItem>
                      <SelectItem value="semaine">{language === 'fr' ? '/semaine' : '/week'}</SelectItem>
                      <SelectItem value="personne">{language === 'fr' ? '/pers.' : '/person'}</SelectItem>
                      <SelectItem value="unite">{language === 'fr' ? '/unité' : '/unit'}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label>{language === 'fr' ? 'Localisation' : 'Location'}</Label>
                <Input
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="Charlevoix, QC"
                  className="bg-background"
                />
              </div>

              <div className="col-span-2">
                <Label>{language === 'fr' ? 'Description *' : 'Description *'}</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder={language === 'fr' 
                    ? 'Décrivez votre offre en détail...'
                    : 'Describe your offer in detail...'}
                  className="bg-background min-h-[100px]"
                />
              </div>

              <div className="col-span-2">
                <Label>{language === 'fr' ? 'Espèces concernées' : 'Target Species'}</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {SPECIES_OPTIONS.map((species) => (
                    <button
                      key={species.value}
                      type="button"
                      onClick={() => handleSpeciesToggle(species.value)}
                      className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                        formData.species.includes(species.value)
                          ? 'bg-[#f5a623] text-black'
                          : 'bg-background border border-border text-gray-400 hover:border-[#f5a623]'
                      }`}
                    >
                      {species.icon} {species.label[language]}
                    </button>
                  ))}
                </div>
              </div>

              <div className="col-span-2">
                <Label>{language === 'fr' ? 'Règles et conditions' : 'Rules and conditions'}</Label>
                <Textarea
                  value={formData.rules}
                  onChange={(e) => setFormData({ ...formData, rules: e.target.value })}
                  placeholder={language === 'fr'
                    ? 'Règles spécifiques, équipement requis, etc.'
                    : 'Specific rules, required equipment, etc.'}
                  className="bg-background min-h-[80px]"
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowModal(false)}>
              {language === 'fr' ? 'Annuler' : 'Cancel'}
            </Button>
            <Button className="btn-golden text-black" onClick={handleSubmit}>
              <Save className="h-4 w-4 mr-2" />
              {editingOffer 
                ? (language === 'fr' ? 'Enregistrer' : 'Save')
                : (language === 'fr' ? 'Créer l\'offre' : 'Create Offer')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PartnerOffers;
