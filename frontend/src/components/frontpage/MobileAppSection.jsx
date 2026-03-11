import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Smartphone, Download, Star, CheckCircle, MapPin, Bell,
  Compass, CloudSun, Camera, Share2
} from 'lucide-react';
import { motion } from 'framer-motion';

const MobileAppSection = () => {
  const features = [
    { icon: MapPin, title: 'GPS Hors-ligne', desc: 'Cartes téléchargeables' },
    { icon: CloudSun, title: 'Météo Temps Réel', desc: 'Alertes conditions optimales' },
    { icon: Bell, title: 'Notifications', desc: 'Activité sur vos territoires' },
    { icon: Camera, title: 'Journal de Chasse', desc: 'Photos et observations' },
  ];

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0d1117]" data-testid="mobile-app-section">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center gap-3 mb-4">
              <Smartphone className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Application Mobile</span>
            </div>
            
            <h2 className="font-barlow text-3xl md:text-5xl font-bold text-white uppercase tracking-tight mb-4">
              BIONIC™ dans <span className="text-[#f5a623]">votre poche</span>
            </h2>
            
            <p className="text-gray-300 text-lg mb-8">
              Accédez à tous vos outils de chasse où que vous soyez. GPS hors-ligne, météo en temps réel, 
              et votre territoire toujours à portée de main.
            </p>

            {/* Features Grid */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              {features.map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="flex items-start gap-3"
                >
                  <div className="p-2 bg-[#f5a623]/10 rounded-sm">
                    <feature.icon className="h-5 w-5 text-[#f5a623]" />
                  </div>
                  <div>
                    <p className="text-white font-semibold">{feature.title}</p>
                    <p className="text-gray-500 text-sm">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Stats */}
            <div className="flex items-center gap-6 mb-8">
              <div className="flex items-center gap-2">
                <div className="flex">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-[#f5a623] fill-[#f5a623]" />
                  ))}
                </div>
                <span className="text-white font-semibold">4.9</span>
              </div>
              <div className="text-gray-300 text-sm">
                <span className="text-white font-semibold">25K+</span> téléchargements
              </div>
            </div>

            {/* Download Buttons */}
            <div className="flex flex-wrap gap-4">
              <Button className="bg-black border border-white/20 text-white hover:bg-white/10 rounded-lg px-6 py-6">
                <div className="flex items-center gap-3">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                  </svg>
                  <div className="text-left">
                    <p className="text-xs text-gray-300">Télécharger sur</p>
                    <p className="font-semibold">App Store</p>
                  </div>
                </div>
              </Button>
              
              <Button className="bg-black border border-white/20 text-white hover:bg-white/10 rounded-lg px-6 py-6">
                <div className="flex items-center gap-3">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 20.5v-17c0-.59.34-1.11.84-1.35L13.69 12l-9.85 9.85c-.5-.24-.84-.76-.84-1.35zm13.81-5.38L6.05 21.34l8.49-8.49 2.27 2.27zm3.35-4.31c.34.27.59.69.59 1.19s-.22.9-.57 1.18l-2.29 1.32-2.5-2.5 2.5-2.5 2.27 1.31zM6.05 2.66l10.76 6.22-2.27 2.27-8.49-8.49z"/>
                  </svg>
                  <div className="text-left">
                    <p className="text-xs text-gray-300">Disponible sur</p>
                    <p className="font-semibold">Google Play</p>
                  </div>
                </div>
              </Button>
            </div>
          </motion.div>

          {/* Phone Mockup */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative flex justify-center"
          >
            <div className="relative">
              {/* Glow effect */}
              <div className="absolute inset-0 bg-[#f5a623]/20 blur-3xl rounded-full" />
              
              {/* Phone frame */}
              <div className="relative bg-[#1a1a1a] rounded-[3rem] p-3 border border-white/10 shadow-2xl">
                <div className="bg-black rounded-[2.5rem] overflow-hidden w-[280px] h-[560px]">
                  {/* Status bar */}
                  <div className="bg-black px-6 py-2 flex items-center justify-between">
                    <span className="text-white text-xs font-medium">9:41</span>
                    <div className="flex items-center gap-1">
                      <div className="w-4 h-2 bg-white/60 rounded-sm" />
                      <div className="w-4 h-2 bg-white/60 rounded-sm" />
                      <div className="w-6 h-3 bg-[#f5a623] rounded-sm" />
                    </div>
                  </div>
                  
                  {/* App content simulation */}
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-[#f5a623] rounded-full flex items-center justify-center">
                          <Compass className="h-4 w-4 text-black" />
                        </div>
                        <span className="text-white font-bold">BIONIC™</span>
                      </div>
                      <Bell className="h-5 w-5 text-gray-300" />
                    </div>
                    
                    {/* Map preview */}
                    <div className="bg-[#0d1117] rounded-lg h-40 mb-4 overflow-hidden relative">
                      <img 
                        src="https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png"
                        alt="Map preview"
                        className="w-full h-full object-cover opacity-60"
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-4 h-4 bg-[#f5a623] rounded-full animate-ping" />
                        <div className="absolute w-4 h-4 bg-[#f5a623] rounded-full" />
                      </div>
                    </div>
                    
                    {/* Weather widget */}
                    <div className="bg-[#1a1a1a] rounded-lg p-3 mb-4 border border-white/5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-gray-300 text-xs">Laurentides</p>
                          <p className="text-white text-2xl font-bold">-5°C</p>
                        </div>
                        <CloudSun className="h-10 w-10 text-[#f5a623]" />
                      </div>
                      <Badge className="mt-2 bg-green-500/20 text-green-400 text-xs">
                        Conditions optimales
                      </Badge>
                    </div>
                    
                    {/* Quick actions */}
                    <div className="grid grid-cols-4 gap-2">
                      {[MapPin, Camera, Compass, Share2].map((Icon, i) => (
                        <div key={i} className="bg-[#1a1a1a] rounded-lg p-3 flex items-center justify-center border border-white/5">
                          <Icon className="h-5 w-5 text-gray-300" />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Home indicator */}
                <div className="absolute bottom-1 left-1/2 -translate-x-1/2 w-32 h-1 bg-white/30 rounded-full" />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default MobileAppSection;
