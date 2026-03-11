/**
 * BecomePartner - Partner application form component
 * Allows potential partners to submit their partnership request
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Handshake,
  Building2,
  User,
  Mail,
  Phone,
  Globe,
  FileText,
  Package,
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  Send,
  Shield,
  Clock,
  Star,
  Users,
  TrendingUp,
  Calendar,
  Tag,
  Tent,
  TreePine,
  Crosshair,
  Store,
  Wrench,
  Factory,
  Fish,
  ClipboardList
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

const API = process.env.REACT_APP_BACKEND_URL;

// Partner type icons - BIONIC Design System Compliant (no emojis)
const PARTNER_TYPE_ICONS = {
  marques: 'tag',
  pourvoiries: 'tent',
  proprietaires: 'tree-pine',
  guides: 'crosshair',
  boutiques: 'store',
  services: 'wrench',
  fabricants: 'factory',
  zec: 'deer',
  clubs: 'fish',
  particuliers: 'user',
  autres: 'clipboard-list'
};

const BecomePartner = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [partnerTypes, setPartnerTypes] = useState([]);
  
  const [formData, setFormData] = useState({
    company_name: '',
    partner_type: '',
    contact_name: '',
    email: '',
    phone: '',
    website: '',
    description: '',
    products_services: '',
    legal_consent: false,
    preferred_language: language
  });
  
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchPartnerTypes();
  }, []);

  useEffect(() => {
    setFormData(prev => ({ ...prev, preferred_language: language }));
  }, [language]);

  const fetchPartnerTypes = async () => {
    try {
      const response = await axios.get(`${API}/api/partnership/types`);
      setPartnerTypes(response.data.types);
    } catch (error) {
      console.error('Error fetching partner types:', error);
    }
  };

  const validateStep1 = () => {
    const newErrors = {};
    if (!formData.company_name.trim()) newErrors.company_name = language === 'fr' ? 'Nom requis' : 'Name required';
    if (!formData.partner_type) newErrors.partner_type = language === 'fr' ? 'Type requis' : 'Type required';
    if (!formData.contact_name.trim()) newErrors.contact_name = language === 'fr' ? 'Contact requis' : 'Contact required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};
    if (!formData.email.trim()) {
      newErrors.email = language === 'fr' ? 'Courriel requis' : 'Email required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = language === 'fr' ? 'Courriel invalide' : 'Invalid email';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = language === 'fr' ? 'Téléphone requis' : 'Phone required';
    } else if (formData.phone.replace(/\D/g, '').length < 10) {
      newErrors.phone = language === 'fr' ? 'Téléphone invalide' : 'Invalid phone';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = () => {
    const newErrors = {};
    if (!formData.description.trim() || formData.description.length < 20) {
      newErrors.description = language === 'fr' ? 'Description trop courte (min 20 caractères)' : 'Description too short (min 20 characters)';
    }
    if (!formData.products_services.trim() || formData.products_services.length < 10) {
      newErrors.products_services = language === 'fr' ? 'Détaillez vos produits/services' : 'Detail your products/services';
    }
    if (!formData.legal_consent) {
      newErrors.legal_consent = language === 'fr' ? 'Consentement requis' : 'Consent required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) setStep(2);
    else if (step === 2 && validateStep2()) setStep(3);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep3()) return;
    
    setLoading(true);
    try {
      await axios.post(`${API}/api/partnership/request`, formData);
      setSubmitted(true);
      toast.success(language === 'fr' ? 'Demande envoyée avec succès!' : 'Request submitted successfully!');
    } catch (error) {
      const message = error.response?.data?.detail || (language === 'fr' ? 'Erreur lors de l\'envoi' : 'Error submitting request');
      toast.error(message);
    }
    setLoading(false);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  // Success screen
  if (submitted) {
    return (
      <main className="min-h-screen bg-background pt-20 pb-16">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="bg-card border-border overflow-hidden">
            <div className="bg-gradient-to-r from-green-600 to-green-500 p-8 text-center">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-10 w-10 text-green-600" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-2">
                {language === 'fr' ? 'Demande envoyée!' : 'Request Submitted!'}
              </h1>
              <p className="text-green-100">
                {language === 'fr' 
                  ? 'Merci pour votre intérêt à devenir partenaire'
                  : 'Thank you for your interest in becoming a partner'}
              </p>
            </div>
            <CardContent className="p-8 text-center">
              <div className="space-y-6">
                <div className="bg-background/50 rounded-lg p-6 border border-border">
                  <Clock className="h-8 w-8 text-[#f5a623] mx-auto mb-3" />
                  <h3 className="text-white font-semibold mb-2">
                    {language === 'fr' ? 'Prochaines étapes' : 'Next Steps'}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    {language === 'fr'
                      ? 'Notre équipe examinera votre demande et vous contactera sous 48 à 72 heures ouvrables.'
                      : 'Our team will review your request and contact you within 48 to 72 business hours.'}
                  </p>
                </div>
                
                <div className="bg-background/50 rounded-lg p-6 border border-border">
                  <Mail className="h-8 w-8 text-[#f5a623] mx-auto mb-3" />
                  <h3 className="text-white font-semibold mb-2">
                    {language === 'fr' ? 'Vérifiez vos courriels' : 'Check your email'}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    {language === 'fr'
                      ? `Un courriel de confirmation a été envoyé à ${formData.email}`
                      : `A confirmation email has been sent to ${formData.email}`}
                  </p>
                </div>
                
                <Button 
                  onClick={() => navigate('/')} 
                  className="btn-golden text-black font-semibold"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  {language === 'fr' ? 'Retour à l\'accueil' : 'Back to home'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <Button 
            variant="ghost" 
            className="mb-4 text-gray-400 hover:text-white"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {language === 'fr' ? 'Retour' : 'Back'}
          </Button>
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#f5a623] to-[#d4891c] flex items-center justify-center">
              <Handshake className="h-8 w-8 text-black" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            {language === 'fr' ? 'Devenez Partenaire' : 'Become a Partner'}
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            {language === 'fr'
              ? 'Rejoignez notre réseau de partenaires et développez votre activité avec Bionic™'
              : 'Join our partner network and grow your business with Bionic™'}
          </p>
        </div>

        {/* Benefits */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: TrendingUp, label: language === 'fr' ? 'Croissance' : 'Growth', desc: language === 'fr' ? 'Augmentez vos ventes' : 'Increase sales' },
            { icon: Users, label: language === 'fr' ? 'Visibilité' : 'Visibility', desc: language === 'fr' ? 'Milliers de clients' : 'Thousands of clients' },
            { icon: Calendar, label: language === 'fr' ? 'Calendrier' : 'Calendar', desc: language === 'fr' ? 'Réservations directes' : 'Direct bookings' },
            { icon: Shield, label: language === 'fr' ? 'Sécurité' : 'Security', desc: language === 'fr' ? 'Paiements garantis' : 'Guaranteed payments' },
          ].map((item, i) => (
            <Card key={i} className="bg-card/50 border-border p-4 text-center">
              <item.icon className="h-6 w-6 text-[#f5a623] mx-auto mb-2" />
              <p className="text-white font-medium text-sm">{item.label}</p>
              <p className="text-gray-500 text-xs">{item.desc}</p>
            </Card>
          ))}
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <React.Fragment key={s}>
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                  step >= s 
                    ? 'bg-[#f5a623] text-black' 
                    : 'bg-gray-800 text-gray-500'
                }`}
              >
                {step > s ? <CheckCircle className="h-5 w-5" /> : s}
              </div>
              {s < 3 && (
                <div className={`w-16 h-1 rounded ${step > s ? 'bg-[#f5a623]' : 'bg-gray-800'}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Form Card */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              {step === 1 && <><Building2 className="h-5 w-5 text-[#f5a623]" /> {language === 'fr' ? 'Informations entreprise' : 'Company Information'}</>}
              {step === 2 && <><User className="h-5 w-5 text-[#f5a623]" /> {language === 'fr' ? 'Coordonnées' : 'Contact Details'}</>}
              {step === 3 && <><FileText className="h-5 w-5 text-[#f5a623]" /> {language === 'fr' ? 'Description du partenariat' : 'Partnership Description'}</>}
            </CardTitle>
            <CardDescription>
              {language === 'fr' ? `Étape ${step} sur 3` : `Step ${step} of 3`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Step 1: Company Info */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Nom de l\'entreprise *' : 'Company Name *'}</Label>
                  <Input
                    value={formData.company_name}
                    onChange={(e) => handleChange('company_name', e.target.value)}
                    placeholder={language === 'fr' ? 'Votre entreprise' : 'Your company'}
                    className={`bg-background ${errors.company_name ? 'border-red-500' : ''}`}
                    data-testid="partner-company-name"
                  />
                  {errors.company_name && <p className="text-red-500 text-xs mt-1">{errors.company_name}</p>}
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Type de partenaire *' : 'Partner Type *'}</Label>
                  <Select 
                    value={formData.partner_type} 
                    onValueChange={(value) => handleChange('partner_type', value)}
                  >
                    <SelectTrigger className={`bg-background ${errors.partner_type ? 'border-red-500' : ''}`} data-testid="partner-type-select">
                      <SelectValue placeholder={language === 'fr' ? 'Sélectionnez un type' : 'Select a type'} />
                    </SelectTrigger>
                    <SelectContent>
                      {partnerTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          <span className="flex items-center gap-2">
                            <span>{PARTNER_TYPE_ICONS[type.value]}</span>
                            <span>{language === 'fr' ? type.label_fr : type.label_en}</span>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.partner_type && <p className="text-red-500 text-xs mt-1">{errors.partner_type}</p>}
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Nom du contact principal *' : 'Primary Contact Name *'}</Label>
                  <Input
                    value={formData.contact_name}
                    onChange={(e) => handleChange('contact_name', e.target.value)}
                    placeholder={language === 'fr' ? 'Jean Dupont' : 'John Doe'}
                    className={`bg-background ${errors.contact_name ? 'border-red-500' : ''}`}
                    data-testid="partner-contact-name"
                  />
                  {errors.contact_name && <p className="text-red-500 text-xs mt-1">{errors.contact_name}</p>}
                </div>
              </div>
            )}

            {/* Step 2: Contact Details */}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Courriel *' : 'Email *'}</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                    <Input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      placeholder="contact@entreprise.com"
                      className={`bg-background pl-10 ${errors.email ? 'border-red-500' : ''}`}
                      data-testid="partner-email"
                    />
                  </div>
                  {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Téléphone *' : 'Phone *'}</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                    <Input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleChange('phone', e.target.value)}
                      placeholder="(514) 555-1234"
                      className={`bg-background pl-10 ${errors.phone ? 'border-red-500' : ''}`}
                      data-testid="partner-phone"
                    />
                  </div>
                  {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Site web (optionnel)' : 'Website (optional)'}</Label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                    <Input
                      type="url"
                      value={formData.website}
                      onChange={(e) => handleChange('website', e.target.value)}
                      placeholder="https://www.votresite.com"
                      className="bg-background pl-10"
                      data-testid="partner-website"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Langue préférée' : 'Preferred Language'}</Label>
                  <Select 
                    value={formData.preferred_language} 
                    onValueChange={(value) => handleChange('preferred_language', value)}
                  >
                    <SelectTrigger className="bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fr">🇨🇦 Français</SelectItem>
                      <SelectItem value="en">🇬🇧 English</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {/* Step 3: Partnership Description */}
            {step === 3 && (
              <div className="space-y-4">
                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Description du partenariat souhaité *' : 'Desired Partnership Description *'}</Label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder={language === 'fr' 
                      ? 'Décrivez votre entreprise et le type de partenariat que vous recherchez...'
                      : 'Describe your business and the type of partnership you are looking for...'}
                    className={`bg-background min-h-[120px] ${errors.description ? 'border-red-500' : ''}`}
                    data-testid="partner-description"
                  />
                  <p className="text-gray-500 text-xs mt-1">{formData.description.length}/2000</p>
                  {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}
                </div>

                <div>
                  <Label className="text-gray-300">{language === 'fr' ? 'Produits / Services proposés *' : 'Products / Services Offered *'}</Label>
                  <Textarea
                    value={formData.products_services}
                    onChange={(e) => handleChange('products_services', e.target.value)}
                    placeholder={language === 'fr'
                      ? 'Listez vos principaux produits ou services...'
                      : 'List your main products or services...'}
                    className={`bg-background min-h-[100px] ${errors.products_services ? 'border-red-500' : ''}`}
                    data-testid="partner-products"
                  />
                  {errors.products_services && <p className="text-red-500 text-xs mt-1">{errors.products_services}</p>}
                </div>

                <div className="bg-background/50 rounded-lg p-4 border border-border">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      id="consent"
                      checked={formData.legal_consent}
                      onCheckedChange={(checked) => handleChange('legal_consent', checked)}
                      className="mt-1"
                      data-testid="partner-consent"
                    />
                    <div className="flex-1">
                      <Label htmlFor="consent" className="text-gray-300 text-sm cursor-pointer">
                        {language === 'fr'
                          ? 'J\'accepte les conditions d\'utilisation et la politique de confidentialité de Bionic™. Je consens à ce que mes informations soient traitées pour établir un partenariat commercial.'
                          : 'I accept the terms of use and privacy policy of Bionic™. I consent to having my information processed to establish a commercial partnership.'}
                      </Label>
                      {errors.legal_consent && <p className="text-red-500 text-xs mt-1">{errors.legal_consent}</p>}
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <Card className="bg-background/30 border-border">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm text-gray-400">
                      {language === 'fr' ? 'Récapitulatif' : 'Summary'}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">{language === 'fr' ? 'Entreprise' : 'Company'}</span>
                      <span className="text-white font-medium">{formData.company_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Type</span>
                      <Badge className="bg-[#f5a623]/20 text-[#f5a623]">
                        {PARTNER_TYPE_ICONS[formData.partner_type]} {partnerTypes.find(t => t.value === formData.partner_type)?.[language === 'fr' ? 'label_fr' : 'label_en']}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Contact</span>
                      <span className="text-white">{formData.contact_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">{language === 'fr' ? 'Courriel' : 'Email'}</span>
                      <span className="text-white">{formData.email}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-4 border-t border-border">
              <Button
                variant="outline"
                onClick={step === 1 ? () => navigate('/') : handleBack}
                disabled={loading}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                {step === 1 
                  ? (language === 'fr' ? 'Annuler' : 'Cancel')
                  : (language === 'fr' ? 'Précédent' : 'Previous')}
              </Button>

              {step < 3 ? (
                <Button onClick={handleNext} className="btn-golden text-black">
                  {language === 'fr' ? 'Suivant' : 'Next'}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmit} 
                  className="btn-golden text-black"
                  disabled={loading}
                  data-testid="partner-submit-btn"
                >
                  {loading ? (
                    <>{language === 'fr' ? 'Envoi...' : 'Sending...'}</>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      {language === 'fr' ? 'Soumettre la demande' : 'Submit Request'}
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};

export default BecomePartner;
