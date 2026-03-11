/**
 * FormationsPage - Module V5-ULTIME-FUSION
 * Importé de BIONIC HUNT/Chasse-V2 (commit 886bc5d)
 */

import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ExternalLink, Clock, CheckCircle, BookOpen, Target, Users } from "lucide-react";

const FormationsPage = () => {
  const navigate = useNavigate();
  
  // FédéCP Formation Categories
  const fedecpFormations = [
    {
      id: 'securite',
      title: 'Sécurité à la chasse',
      description: 'Cours obligatoire pour l\'obtention du permis de chasse au Québec.',
      icon: '🛡️',
      duration: '8 heures',
      type: 'Obligatoire',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Maniement sécuritaire des armes', 'Règles de sécurité', 'Éthique du chasseur', 'Réglementation']
    },
    {
      id: 'piegeage',
      title: 'Formation au piégeage',
      description: 'Techniques de piégeage responsable et réglementation.',
      icon: '🪤',
      duration: '6 heures',
      type: 'Spécialisé',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Types de pièges', 'Espèces ciblées', 'Réglementation', 'Éthique']
    },
    {
      id: 'arbalete',
      title: 'Formation arbalète',
      description: 'Utilisation sécuritaire de l\'arbalète pour la chasse.',
      icon: '🏹',
      duration: '4 heures',
      type: 'Spécialisé',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Équipement', 'Technique de tir', 'Sécurité', 'Réglementation']
    },
    {
      id: 'terres-privees',
      title: 'Accès aux terres privées',
      description: 'Bonnes pratiques et ententes chasseur/propriétaire.',
      icon: '🏠',
      duration: '2 heures',
      type: 'Recommandé',
      link: 'https://fedecp.com/la-chasse/je-pratique/ou-chasser/',
      topics: ['Demande d\'autorisation', 'Respect des propriétés', 'Ententes écrites', 'Assurances']
    }
  ];

  // BIONIC™ Internal Formations
  const bionicFormations = [
    {
      id: 'analyse-territoire',
      title: 'Analyse de territoire BIONIC™',
      description: 'Maîtrisez les outils d\'analyse géospatiale pour optimiser vos chasses.',
      icon: '🗺️',
      duration: '3 heures',
      type: 'BIONIC™',
      modules: [
        'Lecture des heatmaps d\'activité',
        'Interprétation des zones de probabilité',
        'Utilisation des couches WMS',
        'Analyse par espèce'
      ]
    },
    {
      id: 'parcours-guide',
      title: 'Parcours guidé optimisé',
      description: 'Apprenez à créer et suivre des parcours de chasse intelligents.',
      icon: '🧭',
      duration: '2 heures',
      type: 'BIONIC™',
      modules: [
        'Création de waypoints stratégiques',
        'Génération de parcours optimisés',
        'Interprétation des probabilités',
        'Navigation GPS terrain'
      ]
    },
    {
      id: 'attractants',
      title: 'Science des attractants',
      description: 'Comprendre la composition et l\'utilisation des produits BIONIC™.',
      icon: '🧪',
      duration: '2 heures',
      type: 'BIONIC™',
      modules: [
        'Types d\'attractants par espèce',
        'Analyse nutritionnelle du gibier',
        'Placement stratégique',
        'Saisons et timing'
      ]
    }
  ];

  return (
    <main className="pt-20 min-h-screen bg-background" data-testid="formations-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header with Back Button */}
        <div className="flex items-center gap-4 mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white"
            data-testid="back-button"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
          <div>
            <h1 className="golden-text text-3xl sm:text-4xl font-bold">Formations</h1>
            <p className="text-gray-400 mt-1">FédéCP & BIONIC™ Academy</p>
          </div>
        </div>

        {/* FédéCP Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <BookOpen className="h-6 w-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Formations FédéCP</h2>
            <a 
              href="https://fedecp.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="ml-auto"
            >
              <Badge className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 cursor-pointer">
                <ExternalLink className="h-3 w-3 mr-1" /> fedecp.com
              </Badge>
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {fedecpFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-blue-500/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <span className="text-3xl">{formation.icon}</span>
                    <Badge className={formation.type === 'Obligatoire' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}>
                      {formation.type}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.topics.map((topic, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-xs text-gray-300">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {topic}
                      </li>
                    ))}
                  </ul>
                  <a href={formation.link} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                      <ExternalLink className="h-3 w-3 mr-2" />
                      Voir sur FédéCP
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* BIONIC™ Academy Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Target className="h-6 w-6 text-[#f5a623]" />
            <h2 className="text-2xl font-bold text-white">BIONIC™ Academy</h2>
            <Badge className="bg-[#f5a623]/20 text-[#f5a623]">
              Bientôt disponible
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {bionicFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-[#f5a623]/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <span className="text-3xl">{formation.icon}</span>
                    <Badge className="bg-[#f5a623]/20 text-[#f5a623]">
                      {formation.type}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.modules.map((module, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-xs text-gray-300">
                        <CheckCircle className="h-3 w-3 text-[#f5a623]" />
                        {module}
                      </li>
                    ))}
                  </ul>
                  <Button size="sm" className="w-full btn-golden text-black" disabled>
                    <Users className="h-3 w-3 mr-2" />
                    Prochainement
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

export default FormationsPage;
