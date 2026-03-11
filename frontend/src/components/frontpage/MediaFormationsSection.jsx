import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, Youtube, Clock, Eye, Calendar, ChevronRight,
  GraduationCap, BookOpen, Award, Users, ExternalLink
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const MediaFormationsSection = () => {
  const [activeVideo, setActiveVideo] = useState(null);

  const videos = [
    {
      id: 'video1',
      title: 'Guide complet: Analyse de territoire BIONIC™',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      duration: '15:42',
      views: '12.5K',
      date: '2 jours',
      youtubeId: 'dQw4w9WgXcQ'
    },
    {
      id: 'video2',
      title: 'Techniques d\'appel orignal - Saison du rut',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      duration: '22:18',
      views: '8.3K',
      date: '1 semaine',
      youtubeId: 'dQw4w9WgXcQ'
    },
    {
      id: 'video3',
      title: 'Installation de caméras de trail - Pro Tips',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      duration: '18:05',
      views: '6.1K',
      date: '2 semaines',
      youtubeId: 'dQw4w9WgXcQ'
    }
  ];

  const formations = [
    {
      id: 'f1',
      title: 'Initiation chasse avec arme à feu',
      provider: 'FédéCP',
      type: 'Obligatoire',
      duration: '8 heures',
      price: '75$',
      icon: GraduationCap
    },
    {
      id: 'f2',
      title: 'Analyse de territoire BIONIC™',
      provider: 'BIONIC™',
      type: 'Exclusif',
      duration: 'Auto-formation',
      price: 'Gratuit',
      icon: Award
    },
    {
      id: 'f3',
      title: 'Formation au piégeage',
      provider: 'FédéCP',
      type: 'Obligatoire',
      duration: '8 heures',
      price: '60$',
      icon: BookOpen
    }
  ];

  return (
    <section className="py-16 px-4 bg-[#0a0a0a]" data-testid="media-formations-section">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Hunt TV Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <Youtube className="h-6 w-6 text-red-500" />
              <div>
                <span className="text-red-500 uppercase tracking-wider text-sm font-bold block">Hunt TV</span>
                <h2 className="font-barlow text-2xl md:text-3xl font-bold text-white uppercase tracking-tight">
                  Vidéos <span className="text-[#f5a623]">Récentes</span>
                </h2>
              </div>
            </div>

            {/* Featured Video */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-4"
            >
              <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group cursor-pointer">
                <div className="relative aspect-video">
                  <img 
                    src={videos[0].thumbnail}
                    alt={videos[0].title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center">
                      <Play className="h-8 w-8 text-white fill-white ml-1" />
                    </div>
                  </div>
                  <div className="absolute bottom-3 right-3 bg-black/80 px-2 py-1 rounded text-white text-sm font-mono">
                    {videos[0].duration}
                  </div>
                </div>
                <CardContent className="p-4">
                  <h3 className="text-white font-semibold text-lg group-hover:text-[#f5a623] transition-colors">
                    {videos[0].title}
                  </h3>
                  <div className="flex items-center gap-4 mt-2 text-gray-300 text-sm">
                    <span className="flex items-center gap-1"><Eye className="h-4 w-4" /> {videos[0].views}</span>
                    <span className="flex items-center gap-1"><Calendar className="h-4 w-4" /> {videos[0].date}</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Video Grid */}
            <div className="grid grid-cols-2 gap-4">
              {videos.slice(1).map((video, i) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group cursor-pointer hover:border-red-500/30 transition-colors">
                    <div className="relative aspect-video">
                      <img 
                        src={video.thumbnail}
                        alt={video.title}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Play className="h-8 w-8 text-white fill-white" />
                      </div>
                      <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-0.5 rounded text-white text-xs font-mono">
                        {video.duration}
                      </div>
                    </div>
                    <CardContent className="p-3">
                      <h3 className="text-white font-medium text-sm line-clamp-2 group-hover:text-red-400 transition-colors">
                        {video.title}
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-gray-500 text-xs">
                        <span>{video.views} vues</span>
                        <span>{video.date}</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            <div className="mt-4 text-center">
              <Button variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/10 rounded-sm">
                <Youtube className="h-4 w-4 mr-2" />
                Voir toutes les vidéos
              </Button>
            </div>
          </div>

          {/* Formations Section */}
          <div>
            <div className="flex items-center gap-3 mb-6">
              <GraduationCap className="h-6 w-6 text-[#f5a623]" />
              <div>
                <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold block">Centre de formation</span>
                <h2 className="font-barlow text-2xl md:text-3xl font-bold text-white uppercase tracking-tight">
                  Formations
                </h2>
              </div>
            </div>

            <div className="space-y-4">
              {formations.map((formation, i) => {
                const Icon = formation.icon;
                return (
                  <motion.div
                    key={formation.id}
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    viewport={{ once: true }}
                  >
                    <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden hover:border-[#f5a623]/30 transition-colors group cursor-pointer">
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className="p-2 bg-[#f5a623]/10 rounded-sm">
                            <Icon className="h-5 w-5 text-[#f5a623]" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge 
                                className={`text-xs ${
                                  formation.type === 'Obligatoire' 
                                    ? 'bg-red-500/20 text-red-400' 
                                    : 'bg-[#f5a623]/20 text-[#f5a623]'
                                }`}
                              >
                                {formation.type}
                              </Badge>
                              <span className="text-gray-500 text-xs">{formation.provider}</span>
                            </div>
                            <h3 className="text-white font-medium group-hover:text-[#f5a623] transition-colors">
                              {formation.title}
                            </h3>
                            <div className="flex items-center gap-3 mt-2 text-gray-300 text-sm">
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" /> {formation.duration}
                              </span>
                              <span className="text-[#f5a623] font-semibold">{formation.price}</span>
                            </div>
                          </div>
                          <ChevronRight className="h-5 w-5 text-gray-500 group-hover:text-[#f5a623] group-hover:translate-x-1 transition-all" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            <Link to="/formations">
              <Button className="w-full mt-4 bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm">
                <BookOpen className="h-4 w-4 mr-2" />
                Voir toutes les formations
              </Button>
            </Link>

            {/* Stats Card */}
            <Card className="mt-4 bg-gradient-to-br from-[#f5a623]/10 to-transparent border-[#f5a623]/20 rounded-md">
              <CardContent className="p-4 text-center">
                <Users className="h-8 w-8 text-[#f5a623] mx-auto mb-2" />
                <div className="font-barlow text-3xl font-bold text-white">2,847</div>
                <p className="text-gray-300 text-sm">Chasseurs formés cette année</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MediaFormationsSection;
