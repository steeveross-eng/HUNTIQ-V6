import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronDown, Play, MapPin, Radar, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { useStatsEngine } from '@/hooks/useStatsEngine';

const HeroSection = () => {
  const [scrollY, setScrollY] = useState(0);
  
  // Use Stats Engine for dynamic values with animation
  const stats = useStatsEngine({
    animationDuration: 1500,
    refreshInterval: 120000, // Refresh every 2 minutes
  });

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section 
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      data-testid="hero-section"
    >
      {/* Background with parallax */}
      <div 
        className="absolute inset-0 z-0"
        style={{ transform: `translateY(${scrollY * 0.5}px)` }}
      >
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ 
            backgroundImage: `url('https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png')`,
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-[#0a0a0a]" />
      </div>

      {/* Scanline effect */}
      <div className="absolute inset-0 z-10 pointer-events-none opacity-20 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />

      {/* Content */}
      <div className="relative z-20 text-center px-4 max-w-5xl mx-auto">
        {/* Logo Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-black/60 backdrop-blur-xl border border-[#f5a623]/30 rounded-sm">
            <Radar className="h-8 w-8 text-[#f5a623]" />
            <span className="font-barlow text-3xl font-bold text-white tracking-wider">BIONIC™</span>
          </div>
        </motion.div>

        {/* Main Title */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="font-barlow text-5xl md:text-7xl lg:text-8xl font-extrabold uppercase tracking-tight mb-6"
        >
          <span className="text-white">La chasse</span>
          <br />
          <span className="text-[#f5a623] drop-shadow-[0_0_30px_rgba(245,166,35,0.5)]">
            réinventée
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-gray-300 text-lg md:text-xl max-w-2xl mx-auto mb-10 font-inter"
        >
          Analyse de territoire • Intelligence artificielle • Données en temps réel
          <br />
          <span className="text-[#f5a623] font-medium">Votre guide vers une chasse parfaite au Québec</span>
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
        >
          <Link to="/territoire">
            <Button 
              className="bg-[#f5a623] text-black hover:bg-[#d9901c] font-bold uppercase tracking-wider px-8 py-6 text-lg rounded-sm shadow-[0_0_20px_rgba(245,166,35,0.4)] hover:shadow-[0_0_30px_rgba(245,166,35,0.6)] transition-all"
              data-testid="hero-cta-territory"
            >
              <MapPin className="mr-2 h-5 w-5" />
              Explorer le territoire
            </Button>
          </Link>
          <Link to="/analyze">
            <Button 
              variant="outline"
              className="border-white/30 text-white hover:bg-white/10 backdrop-blur-md px-8 py-6 text-lg rounded-sm"
              data-testid="hero-cta-analyze"
            >
              <Target className="mr-2 h-5 w-5" />
              Analyser un produit
            </Button>
          </Link>
        </motion.div>

        {/* Stats Bar - Connected to BIONIC™ Stats Engine */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="flex flex-wrap items-center justify-center gap-8 md:gap-12"
        >
          {[
            { value: stats.displayedSubscribers, label: 'Membres abonnés' },
            { value: stats.displayedTerritories, label: 'Territoires analysés' },
            { value: '850+', label: 'Attractants testés' },
            { value: `${stats.satisfaction}%`, label: 'Satisfaction' },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="font-barlow text-3xl md:text-4xl font-bold text-[#f5a623]">{stat.value}</div>
              <div className="text-gray-300 text-sm uppercase tracking-wider">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <ChevronDown className="h-8 w-8 text-[#f5a623]/70" />
        </motion.div>
      </motion.div>
    </section>
  );
};

export default HeroSection;
