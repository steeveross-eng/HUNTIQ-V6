import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Handshake, Building2, MapPin, Phone, ExternalLink,
  Star, CheckCircle, Users, Award, ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';

const PartnersSection = () => {
  const partners = [
    { name: 'FédéCP', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=FédéCP', type: 'Institution' },
    { name: 'SÉPAQ', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=SÉPAQ', type: 'Institution' },
    { name: 'Buck Bomb', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=BuckBomb', type: 'Marque' },
    { name: 'Tink\'s', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=Tinks', type: 'Marque' },
    { name: 'Code Blue', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=CodeBlue', type: 'Marque' },
    { name: 'Wildlife Research', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=WRC', type: 'Marque' },
  ];

  const pourvoiries = [
    {
      id: 1,
      name: 'Pourvoirie du Lac Blanc',
      location: 'Zone 10 - Mauricie',
      rating: 4.9,
      reviews: 156,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      verified: true,
      features: ['Orignal', 'Ours', 'Hébergement']
    },
    {
      id: 2,
      name: 'Domaine Chasseur',
      location: 'Zone 14 - Laurentides',
      rating: 4.8,
      reviews: 98,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      verified: true,
      features: ['Cerf', 'Dindon', 'Guidage']
    },
    {
      id: 3,
      name: 'Pourvoirie Nature Sauvage',
      location: 'Zone 17 - Abitibi',
      rating: 4.7,
      reviews: 72,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      verified: true,
      features: ['Orignal', 'Petit gibier', 'Tout inclus']
    }
  ];

  return (
    <section className="py-16 px-4 bg-[#0a0a0a]" data-testid="partners-section">
      <div className="max-w-7xl mx-auto">
        {/* Partners Logos */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-2">
              <Handshake className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Nos Partenaires</span>
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Réseau de <span className="text-[#f5a623]">Confiance</span>
            </h2>
          </div>

          {/* Logo Grid */}
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {partners.map((partner, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="bg-[#1a1a1a] border border-white/5 rounded-sm p-4 flex items-center justify-center hover:border-[#f5a623]/30 transition-colors cursor-pointer group"
              >
                <div className="text-center">
                  <img 
                    src={partner.logo} 
                    alt={partner.name}
                    className="h-10 object-contain mx-auto opacity-50 group-hover:opacity-100 transition-opacity"
                  />
                  <p className="text-gray-500 text-xs mt-2 group-hover:text-gray-300">{partner.type}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Pourvoiries Section */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Building2 className="h-6 w-6 text-[#f5a623]" />
                <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Pourvoiries Partenaires</span>
              </div>
              <h2 className="font-barlow text-2xl md:text-3xl font-bold text-white uppercase tracking-tight">
                Destinations <span className="text-[#f5a623]">Premium</span>
              </h2>
            </div>
            <Button variant="outline" className="border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10 rounded-sm hidden md:flex">
              Voir toutes les pourvoiries
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {pourvoiries.map((pourvoirie, i) => (
              <motion.div
                key={pourvoirie.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group hover:border-[#f5a623]/30 transition-colors cursor-pointer h-full">
                  {/* Image */}
                  <div className="relative h-40 overflow-hidden">
                    <img 
                      src={pourvoirie.image}
                      alt={pourvoirie.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    {pourvoirie.verified && (
                      <Badge className="absolute top-3 left-3 bg-green-500/20 text-green-400 border-green-500/30">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Vérifié
                      </Badge>
                    )}
                  </div>

                  <CardContent className="p-4">
                    <h3 className="text-white font-semibold text-lg mb-1 group-hover:text-[#f5a623] transition-colors">
                      {pourvoirie.name}
                    </h3>
                    
                    <div className="flex items-center gap-1 text-gray-300 text-sm mb-3">
                      <MapPin className="h-4 w-4" />
                      {pourvoirie.location}
                    </div>

                    {/* Rating */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="flex items-center">
                        <Star className="h-4 w-4 text-[#f5a623] fill-[#f5a623]" />
                        <span className="text-white font-semibold ml-1">{pourvoirie.rating}</span>
                      </div>
                      <span className="text-gray-500 text-sm">({pourvoirie.reviews} avis)</span>
                    </div>

                    {/* Features */}
                    <div className="flex flex-wrap gap-2">
                      {pourvoirie.features.map((feature, j) => (
                        <Badge key={j} variant="outline" className="border-white/20 text-gray-300 text-xs">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            {[
              { icon: Building2, value: '156', label: 'Pourvoiries' },
              { icon: MapPin, value: '29', label: 'Zones couvertes' },
              { icon: Users, value: '12K+', label: 'Chasseurs satisfaits' },
              { icon: Award, value: '98%', label: 'Taux satisfaction' },
            ].map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="bg-black/40 backdrop-blur-sm border border-white/5 rounded-sm p-4 text-center"
              >
                <stat.icon className="h-6 w-6 text-[#f5a623] mx-auto mb-2" />
                <div className="font-barlow text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-gray-500 text-xs uppercase tracking-wider">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default PartnersSection;
