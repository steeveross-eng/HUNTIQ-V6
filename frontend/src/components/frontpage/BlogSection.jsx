import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, Calendar, Clock, User, ChevronRight, Eye,
  MessageSquare, Share2, Bookmark, TrendingUp, Tag
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const BlogSection = () => {
  const articles = [
    {
      id: 1,
      title: 'Guide complet: Préparer votre territoire pour la saison du rut',
      excerpt: 'Découvrez les meilleures stratégies pour maximiser vos chances pendant la période de reproduction du cerf de Virginie.',
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      author: 'Jean-Pierre Tremblay',
      date: '28 Nov 2025',
      readTime: '8 min',
      category: 'Stratégie',
      views: 3421,
      comments: 45,
      featured: true
    },
    {
      id: 2,
      title: 'Les 10 erreurs à éviter avec les attractants',
      excerpt: 'Une analyse scientifique des erreurs les plus courantes et comment les éviter pour maximiser l\'efficacité.',
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      author: 'Marie Gagnon',
      date: '25 Nov 2025',
      readTime: '5 min',
      category: 'Analyse',
      views: 2156,
      comments: 28,
      featured: false
    },
    {
      id: 3,
      title: 'Météo et comportement: Comprendre le lien',
      excerpt: 'Comment la pression atmosphérique et les fronts météo influencent les déplacements du gibier.',
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      author: 'Marc Bouchard',
      date: '22 Nov 2025',
      readTime: '6 min',
      category: 'Science',
      views: 1834,
      comments: 19,
      featured: false
    },
    {
      id: 4,
      title: 'Nouveaux règlements 2026: Ce qui change',
      excerpt: 'Résumé des modifications réglementaires pour la prochaine saison de chasse au Québec.',
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      author: 'Sophie Lavoie',
      date: '20 Nov 2025',
      readTime: '4 min',
      category: 'Réglementation',
      views: 4521,
      comments: 67,
      featured: false
    }
  ];

  const categories = ['Tous', 'Stratégie', 'Analyse', 'Science', 'Réglementation', 'Équipement'];

  const featuredArticle = articles.find(a => a.featured);
  const regularArticles = articles.filter(a => !a.featured);

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#0d1117] to-[#0a0a0a]" data-testid="blog-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <FileText className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Blog & Articles</span>
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Ressources <span className="text-[#f5a623]">Expert</span>
            </h2>
          </div>
          
          {/* Categories */}
          <div className="hidden md:flex items-center gap-2">
            {categories.slice(0, 4).map((cat, i) => (
              <Badge 
                key={i} 
                variant={i === 0 ? 'default' : 'outline'}
                className={i === 0 
                  ? 'bg-[#f5a623] text-black cursor-pointer' 
                  : 'border-white/20 text-gray-300 hover:border-[#f5a623] hover:text-[#f5a623] cursor-pointer transition-colors'
                }
              >
                {cat}
              </Badge>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Featured Article */}
          {featuredArticle && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="lg:col-span-2"
            >
              <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group hover:border-[#f5a623]/30 transition-colors cursor-pointer h-full">
                <div className="relative h-64 overflow-hidden">
                  <img 
                    src={featuredArticle.image}
                    alt={featuredArticle.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                  <Badge className="absolute top-4 left-4 bg-[#f5a623] text-black font-bold">
                    À la une
                  </Badge>
                  <div className="absolute bottom-4 left-4 right-4">
                    <Badge variant="outline" className="border-white/30 text-white mb-3">
                      <Tag className="h-3 w-3 mr-1" />
                      {featuredArticle.category}
                    </Badge>
                    <h3 className="text-white font-bold text-2xl mb-2 group-hover:text-[#f5a623] transition-colors">
                      {featuredArticle.title}
                    </h3>
                    <p className="text-gray-300 line-clamp-2">{featuredArticle.excerpt}</p>
                  </div>
                </div>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-gray-300 text-sm">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" /> {featuredArticle.author}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" /> {featuredArticle.date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" /> {featuredArticle.readTime}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-gray-500 text-sm">
                      <span className="flex items-center gap-1">
                        <Eye className="h-4 w-4" /> {featuredArticle.views.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" /> {featuredArticle.comments}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Regular Articles */}
          <div className="space-y-4">
            {regularArticles.map((article, i) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group hover:border-[#f5a623]/30 transition-colors cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex gap-4">
                      <img 
                        src={article.image}
                        alt={article.title}
                        className="w-24 h-24 rounded-sm object-cover flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <Badge variant="outline" className="border-white/20 text-gray-300 text-xs mb-2">
                          {article.category}
                        </Badge>
                        <h3 className="text-white font-semibold text-sm line-clamp-2 group-hover:text-[#f5a623] transition-colors">
                          {article.title}
                        </h3>
                        <div className="flex items-center gap-3 mt-2 text-gray-500 text-xs">
                          <span>{article.date}</span>
                          <span>{article.readTime}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-10">
          <Button variant="outline" className="border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10 rounded-sm px-8">
            <FileText className="h-4 w-4 mr-2" />
            Voir tous les articles
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </section>
  );
};

export default BlogSection;
