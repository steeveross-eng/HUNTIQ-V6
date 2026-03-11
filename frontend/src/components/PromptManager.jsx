/**
 * PromptManager - Admin component for managing AI prompts
 * Extracted from App.js for better maintainability
 */

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Edit, Trash2, Save, RefreshCw, Eye, Copy, Sparkles, ChevronDown, ChevronUp, Loader2, FolderOpen, Download, FileText, BookOpen, CheckCircle, Target, Link as LinkIcon, Package } from "lucide-react";
import { toast } from "sonner";
import { useLanguage } from '@/contexts/LanguageContext';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PromptManager = () => {
  const [promptData, setPromptData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [saving, setSaving] = useState(false);
  const [saveHistory, setSaveHistory] = useState(null);

  // Application features documentation - auto-generated
  const generatePromptDoc = () => {
    const now = new Date();
    return {
      app_name: "Chasse Bionic™ / BIONIC™",
      version: "2.0.0",
      last_updated: now.toISOString(),
      description: "Application d'analyse de territoire de chasse avec IA, cartographie interactive et recommandations de produits BIONIC™",
      
      modules: [
        {
          name: "Module E-Commerce",
          path: "/",
          features: [
            "Catalogue de produits avec classement par score",
            "Panier d'achat interactif",
            "Système dropshipping + affiliation hybride",
            "Catégorisation automatique des produits",
            "Gestion des fournisseurs partenaires"
          ]
        },
        {
          name: "Module Analyseur",
          path: "/analyzer",
          features: [
            "Analyse de produits avec IA (GPT-4)",
            "Comparaison multi-produits",
            "Catégories et sous-catégories d'analyse",
            "Rapports détaillés par email (Resend)"
          ]
        },
        {
          name: "Module Territoire BIONIC™",
          path: "/territory",
          features: [
            "Carte interactive Leaflet avec couches multiples",
            "Connexion automatique par IP",
            "Analyse GPS (formats Décimal et DMS)",
            "Échelles de carte (1:1000, 1:3000, 1:5000)",
            "Barre d'outils carte: Marqueur, Route, Couches, Mesure, Vue",
            "Upload photos avec reconnaissance d'espèces IA (GPT-4 Vision)",
            "Cartes géologiques du Québec (WMS gouvernemental)",
            "Couverture forestière, Hydrographie, Relief LiDAR, Routes",
            "Analyse par espèce (orignal, chevreuil, ours)",
            "Probabilité de présence basée sur règles métier",
            "Zones de refuge et zones de fraîcheur",
            "Navigation GPS style Avenza avec tracé temps réel",
            "Waypoints personnalisés",
            "Import/Export GPX (Avenza, Garmin compatible)",
            "Analyse nutritionnelle du gibier",
            "Recommandations produits BIONIC™ avec scoring"
          ]
        },
        {
          name: "Module Administration",
          path: "/admin",
          features: [
            "Tableau de bord avec statistiques",
            "Gestion des ventes et commandes",
            "Gestion des produits CRUD",
            "Gestion des partenaires/fournisseurs",
            "Gestion des clients",
            "Suivi des commissions",
            "Rapports de performance",
            "Gestionnaire de catégories d'analyse",
            "Dossier PROMPT avec documentation auto-mise à jour"
          ]
        }
      ],

      api_endpoints: {
        ecommerce: [
          "GET /api/products/top - Produits triés par score",
          "GET /api/products/{id} - Détail produit",
          "POST /api/orders - Créer commande",
          "GET /api/customers - Liste clients"
        ],
        analysis: [
          "POST /api/analyze - Analyse produit IA",
          "GET /api/categories - Catégories d'analyse",
          "POST /api/send-report - Envoyer rapport email"
        ],
        territory: [
          "GET /api/territory/users/auto-login - Connexion auto IP",
          "POST /api/territory/events - Créer observation",
          "GET /api/territory/events/recent - Événements récents",
          "POST /api/territory/photos/upload - Upload photo + IA",
          "GET /api/territory/cameras - Liste caméras",
          "POST /api/territory/analysis/probability - Calcul probabilité",
          "GET /api/territory/analysis/cooling-zones - Zones fraîcheur",
          "POST /api/territory/analysis/nutrition - Analyse nutrition + produits",
          "POST /api/territory/waypoints - Créer waypoint",
          "GET /api/territory/waypoints - Liste waypoints",
          "POST /api/territory/tracks - Démarrer tracé GPS",
          "POST /api/territory/tracks/{id}/points - Ajouter point GPS",
          "POST /api/territory/tracks/{id}/stop - Arrêter tracé",
          "GET /api/territory/export/gpx - Export GPX",
          "POST /api/territory/import/gpx - Import GPX"
        ],
        admin: [
          "POST /api/admin/login - Authentification admin",
          "GET /api/admin/stats - Statistiques globales",
          "GET /api/admin/products - Liste produits admin",
          "PUT /api/admin/products/{id} - Modifier produit",
          "DELETE /api/admin/products/{id} - Supprimer produit"
        ]
      },

      bionic_products: [
        { name: "BIONIC™ Bloc Minéral Premium", category: "minerals", rating: 9.5 },
        { name: "BIONIC™ Mélange Protéiné Forêt", category: "protein", rating: 9.2 },
        { name: "BIONIC™ Attractif Pomme Sauvage", category: "attractant", rating: 8.8 },
        { name: "BIONIC™ Saline Suprême", category: "salt", rating: 9.0 },
        { name: "BIONIC™ Festin de Baies", category: "food", rating: 9.3 },
        { name: "BIONIC™ Boost Panache", category: "minerals", rating: 9.4 }
      ],

      species_rules: {
        orignal: {
          water_distance_optimal_m: 500,
          altitude_range: "200-600m",
          prefers: "zones transition, coulées, flanc SW",
          avoids_roads_within_m: 1000
        },
        chevreuil: {
          water_distance_optimal_m: 300,
          altitude_range: "100-400m",
          prefers: "zones transition, coulées, flanc SW",
          avoids_roads_within_m: 500
        },
        ours: {
          water_distance_optimal_m: 200,
          altitude_range: "100-800m",
          prefers: "coulées, zones isolées",
          avoids_roads_within_m: 2000
        }
      },

      integrations: [
        "OpenAI GPT-4 Vision (reconnaissance espèces)",
        "Emergent LLM Key (clé universelle)",
        "Resend (emails de rapport)",
        "MongoDB (base de données)",
        "Leaflet (cartographie)",
        "WMS Gouvernement Québec (couches géologiques)"
      ],

      tech_stack: {
        frontend: "React 18, TailwindCSS, Shadcn/UI, Leaflet",
        backend: "FastAPI, Python 3.11",
        database: "MongoDB",
        deployment: "Emergent Platform"
      }
    };
  };

  useEffect(() => {
    // Simulate loading and generate prompt
    setLoading(true);
    setTimeout(() => {
      setPromptData(generatePromptDoc());
      setLoading(false);
    }, 500);
  }, []);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      setPromptData(generatePromptDoc());
      setLastUpdate(new Date());
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleCopy = () => {
    const fullPrompt = JSON.stringify(promptData, null, 2);
    navigator.clipboard.writeText(fullPrompt);
    setCopied(true);
    toast.success('Prompt copié dans le presse-papiers!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const fullPrompt = JSON.stringify(promptData, null, 2);
    const blob = new Blob([fullPrompt], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scent_science_prompt_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Fichier téléchargé!');
  };

  const handleRefresh = () => {
    setPromptData(generatePromptDoc());
    setLastUpdate(new Date());
    toast.success('Documentation mise à jour!');
  };

  // Save to database
  const handleSaveToDatabase = async () => {
    if (!promptData) return;
    
    setSaving(true);
    try {
      const response = await axios.post(`${API}/territory/prompt/save`, promptData);
      toast.success(response.data.message || 'Sauvegardé dans la base de données!');
      
      // Refresh save history
      loadSaveHistory();
    } catch (error) {
      toast.error('Erreur lors de la sauvegarde');
      console.error('Save error:', error);
    } finally {
      setSaving(false);
    }
  };

  // Load save history
  const loadSaveHistory = async () => {
    try {
      const response = await axios.get(`${API}/territory/prompt/history`);
      setSaveHistory(response.data);
    } catch (error) {
      console.error('Error loading save history:', error);
    }
  };

  // Load save history on mount
  useEffect(() => {
    loadSaveHistory();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#f5a623]/20 flex items-center justify-center">
                <FolderOpen className="h-6 w-6 text-[#f5a623]" />
              </div>
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  Dossier PROMPT
                  <Badge className="bg-green-500/20 text-green-400">Auto-sync</Badge>
                </CardTitle>
                <CardDescription>
                  Documentation complète et fonctionnalités de l'application
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw className="h-4 w-4 mr-1" />
                Actualiser
              </Button>
              <Button variant="outline" size="sm" onClick={handleCopy}>
                <Copy className="h-4 w-4 mr-1" />
                {copied ? 'Copié!' : 'Copier'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-1" />
                Télécharger
              </Button>
              <Button 
                className="bg-blue-600 hover:bg-blue-700 text-white" 
                size="sm" 
                onClick={handleSaveToDatabase}
                disabled={saving}
              >
                {saving ? (
                  <><Loader2 className="h-4 w-4 mr-1 animate-spin" /> Sauvegarde...</>
                ) : (
                  <><Save className="h-4 w-4 mr-1" /> Sauvegarder BD</>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-gray-400 flex-wrap">
            <span>Version: <span className="text-white">{promptData?.version}</span></span>
            <span>•</span>
            <span>Dernière MAJ: <span className="text-white">{lastUpdate.toLocaleString('fr-CA')}</span></span>
            {saveHistory?.has_saved && (
              <>
                <span>•</span>
                <span className="text-blue-400">
                  BD: {saveHistory.save_count} sauvegarde{saveHistory.save_count > 1 ? 's' : ''}
                </span>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Modules Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {promptData?.modules?.map((module, idx) => (
          <Card key={idx} className="bg-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-[#f5a623]" />
                {module.name}
              </CardTitle>
              <CardDescription className="text-xs font-mono">{module.path}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {module.features.map((feature, fIdx) => (
                  <li key={fIdx} className="text-sm text-gray-300 flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* BIONIC Products */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Package className="h-5 w-5 text-[#f5a623]" />
            Produits BIONIC™ Référencés
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {promptData?.bionic_products?.map((product, idx) => (
              <div key={idx} className="bg-background rounded-lg p-3 border border-border">
                <p className="text-white text-sm font-medium">{product.name}</p>
                <div className="flex items-center justify-between mt-1">
                  <Badge variant="outline" className="text-xs">{product.category}</Badge>
                  <span className="text-[#f5a623] text-sm font-bold">{product.rating}/10</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Species Rules */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Target className="h-5 w-5 text-[#f5a623]" />
            Règles d'Analyse par Espèce
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(promptData?.species_rules || {}).map(([species, rules]) => (
              <div key={species} className="bg-background rounded-lg p-4 border border-border">
                <h4 className="text-white font-bold capitalize mb-2 flex items-center gap-2">
                  <SpeciesIcon speciesId={species === 'orignal' ? 'moose' : species === 'chevreuil' ? 'deer' : 'bear'} size="sm" />
                  {species}
                </h4>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-400">Eau optimale: <span className="text-white">{rules.water_distance_optimal_m}m</span></p>
                  <p className="text-gray-400">Altitude: <span className="text-white">{rules.altitude_range}</span></p>
                  <p className="text-gray-400">Préfère: <span className="text-white">{rules.prefers}</span></p>
                  <p className="text-gray-400">Évite routes: <span className="text-white">&lt;{rules.avoids_roads_within_m}m</span></p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* API Endpoints */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <LinkIcon className="h-5 w-5 text-[#f5a623]" />
            Endpoints API
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(promptData?.api_endpoints || {}).map(([category, endpoints]) => (
              <div key={category}>
                <h4 className="text-white font-semibold capitalize mb-2">{category}</h4>
                <div className="bg-background rounded-lg p-3 font-mono text-xs space-y-1">
                  {endpoints.map((endpoint, idx) => (
                    <p key={idx} className="text-gray-300">{endpoint}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tech Stack & Integrations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white text-lg">Stack Technique</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(promptData?.tech_stack || {}).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-400 capitalize">{key}:</span>
                  <span className="text-white text-sm">{value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white text-lg">Intégrations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {promptData?.integrations?.map((integration, idx) => (
                <li key={idx} className="text-gray-300 text-sm flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  {integration}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Raw JSON Preview */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-[#f5a623]" />
            Prompt JSON Complet
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="bg-background rounded-lg p-4 text-xs text-gray-300 overflow-auto max-h-96 font-mono">
            {JSON.stringify(promptData, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
};

export default PromptManager;
