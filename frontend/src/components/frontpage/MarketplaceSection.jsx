import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Store, ShoppingBag, Star, TrendingUp, Percent, 
  ArrowRight, Clock, Flame, Sparkles
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const MarketplaceSection = () => {
  const featuredItems = [
    {
      id: 1,
      name: 'Attractant Premium Orignal',
      brand: 'BIONIC™',
      price: 89.99,
      originalPrice: 119.99,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      rating: 4.9,
      reviews: 234,
      badge: 'Bestseller',
      discount: 25
    },
    {
      id: 2,
      name: 'Caméra Trail Pro 4K',
      brand: 'WildView',
      price: 299.99,
      originalPrice: 349.99,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      rating: 4.7,
      reviews: 156,
      badge: 'Nouveau',
      discount: 14
    },
    {
      id: 3,
      name: 'Appeau Orignal Électronique',
      brand: 'CallMaster',
      price: 149.99,
      originalPrice: null,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      rating: 4.8,
      reviews: 89,
      badge: null,
      discount: null
    },
    {
      id: 4,
      name: 'Kit d\'attractants 4 saisons',
      brand: 'BIONIC™',
      price: 199.99,
      originalPrice: 249.99,
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      rating: 4.9,
      reviews: 312,
      badge: 'Pack Économique',
      discount: 20
    }
  ];

  const categories = [
    { name: 'Attractants', count: 156 },
    { name: 'Caméras', count: 43 },
    { name: 'Appeaux', count: 67 },
    { name: 'Accessoires', count: 234 },
  ];

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0d1117]" data-testid="marketplace-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Store className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Marketplace</span>
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Équipement <span className="text-[#f5a623]">Premium</span>
            </h2>
          </div>
          
          <div className="hidden md:flex items-center gap-4">
            {categories.map((cat, i) => (
              <Badge 
                key={i} 
                variant="outline" 
                className="border-white/20 text-gray-300 hover:border-[#f5a623] hover:text-[#f5a623] cursor-pointer transition-colors"
              >
                {cat.name} ({cat.count})
              </Badge>
            ))}
          </div>
        </div>

        {/* Flash Sale Banner */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-[#f5a623]/20 via-[#f5a623]/10 to-transparent border border-[#f5a623]/30 rounded-md p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-[#f5a623] rounded-sm">
                <Flame className="h-6 w-6 text-black" />
              </div>
              <div>
                <p className="text-[#f5a623] font-bold text-lg">VENTE FLASH</p>
                <p className="text-gray-300 text-sm">Jusqu'à 30% sur les attractants BIONIC™</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-gray-300 text-xs">Se termine dans</p>
                <p className="text-white font-mono text-lg">02:34:56</p>
              </div>
              <Button className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm">
                Voir les offres
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredItems.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group hover:border-[#f5a623]/30 transition-all duration-300 h-full">
                {/* Image */}
                <div className="relative aspect-square overflow-hidden">
                  <img 
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  {/* Badge */}
                  {item.badge && (
                    <Badge className="absolute top-3 left-3 bg-[#f5a623] text-black font-bold">
                      {item.badge}
                    </Badge>
                  )}
                  {/* Discount Badge */}
                  {item.discount && (
                    <Badge className="absolute top-3 right-3 bg-red-500 text-white">
                      -{item.discount}%
                    </Badge>
                  )}
                </div>

                <CardContent className="p-4">
                  {/* Brand */}
                  <p className="text-[#f5a623] text-xs uppercase tracking-wider mb-1">{item.brand}</p>
                  
                  {/* Name */}
                  <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2 group-hover:text-[#f5a623] transition-colors">
                    {item.name}
                  </h3>

                  {/* Rating */}
                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, j) => (
                        <Star 
                          key={j} 
                          className={`h-4 w-4 ${j < Math.floor(item.rating) ? 'text-[#f5a623] fill-[#f5a623]' : 'text-gray-600'}`}
                        />
                      ))}
                    </div>
                    <span className="text-gray-300 text-sm">({item.reviews})</span>
                  </div>

                  {/* Price */}
                  <div className="flex items-center gap-2">
                    <span className="text-[#f5a623] font-bold text-xl">${item.price}</span>
                    {item.originalPrice && (
                      <span className="text-gray-500 line-through text-sm">${item.originalPrice}</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <div className="text-center mt-10">
          <Link to="/shop">
            <Button className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm px-8 py-6 text-lg">
              <ShoppingBag className="h-5 w-5 mr-2" />
              Explorer la boutique
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default MarketplaceSection;
