import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, Sparkles, FlaskConical, Target, Zap, TrendingUp,
  ChevronRight, BarChart3, Radar, Atom
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const BentoGridSection = () => {
  const gridItems = [
    {
      id: 'terrain-analysis',
      title: 'Analyse de Terrain',
      description: 'Topographie, couvert forestier, points d\'eau et corridors de déplacement.',
      icon: Target,
      color: 'from-green-500/20 to-green-900/20',
      stats: [
        { label: 'Zones analysées', value: '2,547' },
        { label: 'Points chauds', value: '847' }
      ],
      link: '/territoire',
      size: 'normal'
    },
    {
      id: 'species-featured',
      title: 'Espèces en Vedette',
      description: 'Orignal, cerf de Virginie, ours noir, dindon sauvage et plus.',
      icon: Radar,
      color: 'from-amber-500/20 to-amber-900/20',
      featured: [
        { name: 'Orignal', status: 'Rut actif', image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png' },
        { name: 'Cerf', status: 'Pré-rut', image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png' },
      ],
      link: '/analyze',
      size: 'tall'
    },
    {
      id: 'ai-hunting',
      title: 'Chasse Intelligente',
      description: 'IA GPT-5.2 pour recommandations personnalisées d\'attractants.',
      icon: Brain,
      color: 'from-purple-500/20 to-purple-900/20',
      badge: 'IA BIONIC™',
      stats: [
        { label: 'Analyses IA', value: '15,420' },
        { label: 'Précision', value: '94%' }
      ],
      link: '/analyze',
      size: 'featured'
    },
    {
      id: 'territories',
      title: 'Territoires en Vedette',
      description: 'Les meilleures zones de chasse du Québec sélectionnées par nos experts.',
      icon: TrendingUp,
      color: 'from-blue-500/20 to-blue-900/20',
      territories: [
        { name: 'Réserve Mastigouche', zone: '14', rating: 4.8 },
        { name: 'ZEC Batiscan-Neilson', zone: '17', rating: 4.6 },
        { name: 'Pourvoirie du Lac Blanc', zone: '10', rating: 4.9 },
      ],
      link: '/territoire',
      size: 'wide'
    },
    {
      id: 'attractants',
      title: 'Attractants Analysés',
      description: '13 critères scientifiques pour évaluer chaque produit.',
      icon: FlaskConical,
      color: 'from-[#f5a623]/20 to-[#f5a623]/5',
      stats: [
        { label: 'Produits testés', value: '850+' },
        { label: 'Critères', value: '13' }
      ],
      link: '/analyze',
      size: 'normal'
    }
  ];

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#0d1117] to-[#0a0a0a]" data-testid="bento-grid-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <Atom className="h-6 w-6 text-[#f5a623]" />
            <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Écosystème BIONIC™</span>
          </div>
          <h2 className="font-barlow text-3xl md:text-5xl font-bold text-white uppercase tracking-tight">
            Intelligence <span className="text-[#f5a623]">Tactique</span>
          </h2>
          <p className="text-gray-300 mt-4 max-w-2xl mx-auto">
            Données terrain, météo, IA et analyse — tous vos outils de chasse en un seul endroit.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 auto-rows-[200px]">
          {gridItems.map((item, index) => {
            const Icon = item.icon;
            const sizeClass = {
              'normal': '',
              'tall': 'md:row-span-2',
              'wide': 'md:col-span-2',
              'featured': 'md:col-span-2 md:row-span-2'
            }[item.size];

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className={sizeClass}
              >
                <Card className={`h-full bg-gradient-to-br ${item.color} bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden hover:border-[#f5a623]/30 transition-all duration-300 group cursor-pointer`}>
                  <Link to={item.link} className="h-full">
                    <CardContent className="p-6 h-full flex flex-col">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="p-2 bg-white/5 rounded-sm">
                          <Icon className="h-6 w-6 text-[#f5a623]" />
                        </div>
                        {item.badge && (
                          <Badge className="bg-[#f5a623]/20 text-[#f5a623] border-[#f5a623]/30">
                            <Sparkles className="h-3 w-3 mr-1" />
                            {item.badge}
                          </Badge>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1">
                        <h3 className="font-barlow text-xl font-bold text-white uppercase tracking-tight mb-2 group-hover:text-[#f5a623] transition-colors">
                          {item.title}
                        </h3>
                        <p className="text-gray-300 text-sm">{item.description}</p>

                        {/* Stats */}
                        {item.stats && (
                          <div className="flex gap-6 mt-4">
                            {item.stats.map((stat, i) => (
                              <div key={i}>
                                <div className="font-barlow text-2xl font-bold text-[#f5a623]">{stat.value}</div>
                                <div className="text-gray-500 text-xs uppercase">{stat.label}</div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Featured Species */}
                        {item.featured && (
                          <div className="mt-4 space-y-2">
                            {item.featured.map((species, i) => (
                              <div key={i} className="flex items-center gap-3 bg-black/30 rounded-sm p-2">
                                <img 
                                  src={species.image} 
                                  alt={species.name} 
                                  className="w-10 h-10 rounded-sm object-cover"
                                />
                                <div>
                                  <p className="text-white font-medium text-sm">{species.name}</p>
                                  <p className="text-[#f5a623] text-xs">{species.status}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Territories List */}
                        {item.territories && (
                          <div className="mt-4 space-y-2">
                            {item.territories.map((territory, i) => (
                              <div key={i} className="flex items-center justify-between bg-black/30 rounded-sm p-2">
                                <div>
                                  <p className="text-white font-medium text-sm">{territory.name}</p>
                                  <p className="text-gray-500 text-xs">Zone {territory.zone}</p>
                                </div>
                                <Badge className="bg-[#f5a623]/20 text-[#f5a623]">
                                  ★ {territory.rating}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Footer */}
                      <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                        <span className="text-[#f5a623] text-sm font-medium group-hover:underline">Explorer</span>
                        <ChevronRight className="h-4 w-4 text-[#f5a623] group-hover:translate-x-1 transition-transform" />
                      </div>
                    </CardContent>
                  </Link>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default BentoGridSection;
