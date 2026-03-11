import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronLeft, ChevronRight, ShoppingCart, Star, TrendingUp, Flame } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useEmblaCarousel from 'embla-carousel-react';
import { ProductsService } from '@/services';

const ProductCarousel = ({ onAddToCart }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [emblaRef, emblaApi] = useEmblaCarousel({ 
    loop: true, 
    align: 'start',
    slidesToScroll: 1 
  });
  const [canScrollPrev, setCanScrollPrev] = useState(false);
  const [canScrollNext, setCanScrollNext] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const data = await ProductsService.getTop(10);
        setProducts(data);
      } catch (err) {
        console.error('Error fetching products:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const onSelect = useCallback(() => {
    if (!emblaApi) return;
    setCanScrollPrev(emblaApi.canScrollPrev());
    setCanScrollNext(emblaApi.canScrollNext());
  }, [emblaApi]);

  useEffect(() => {
    if (!emblaApi) return;
    emblaApi.on('select', onSelect);
    onSelect();
  }, [emblaApi, onSelect]);

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  return (
    <section className="py-16 px-4 bg-[#0a0a0a]" data-testid="product-carousel-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Flame className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Produits vedettes</span>
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Attractants <span className="text-[#f5a623]">BIONIC™</span>
            </h2>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={scrollPrev}
              disabled={!canScrollPrev}
              className="border-white/20 text-white hover:bg-white/10 rounded-sm disabled:opacity-30"
              data-testid="carousel-prev"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={scrollNext}
              disabled={!canScrollNext}
              className="border-white/20 text-white hover:bg-white/10 rounded-sm disabled:opacity-30"
              data-testid="carousel-next"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Carousel */}
        <div className="overflow-hidden" ref={emblaRef}>
          <div className="flex gap-4">
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                className="flex-[0_0_280px] md:flex-[0_0_300px]"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden hover:border-[#f5a623]/50 transition-all duration-300 group h-full">
                  {/* Image */}
                  <div className="relative aspect-square overflow-hidden">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    {/* Rank Badge */}
                    <div className="absolute top-3 left-3">
                      <Badge className="bg-[#f5a623] text-black font-bold px-3 py-1">
                        #{product.rank || index + 1}
                      </Badge>
                    </div>
                    {/* Score Badge */}
                    <div className="absolute top-3 right-3">
                      <Badge className="bg-black/60 backdrop-blur-sm text-white flex items-center gap-1">
                        <Star className="h-3 w-3 text-[#f5a623] fill-[#f5a623]" />
                        {product.score || 85}
                      </Badge>
                    </div>
                    {/* Hover Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>

                  <CardContent className="p-4">
                    <p className="text-[#f5a623] text-xs uppercase tracking-wider mb-1">{product.brand}</p>
                    <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2">{product.name}</h3>
                    
                    {/* Price & Action */}
                    <div className="flex items-center justify-between mt-4">
                      <span className="text-[#f5a623] font-bold text-xl">${product.price}</span>
                      <Button
                        size="sm"
                        className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
                        onClick={() => onAddToCart?.(product)}
                        data-testid={`add-to-cart-${product.id}`}
                      >
                        <ShoppingCart className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* View All Link */}
        <div className="text-center mt-8">
          <Button
            variant="outline"
            className="border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10 rounded-sm px-8"
            asChild
          >
            <a href="/shop" data-testid="view-all-products">
              Voir tous les produits
              <TrendingUp className="ml-2 h-4 w-4" />
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default ProductCarousel;
