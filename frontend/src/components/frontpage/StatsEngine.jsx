/**
 * BIONIC™ Stats Engine - Components
 * 
 * Composants visuels pour afficher les statistiques:
 * - StatBlock: Bloc individuel avec valeur et label
 * - StatsPanel: Grille complète des statistiques
 */

import { motion } from 'framer-motion';
import { 
  Users, MapPin, Target, Beaker, ThumbsUp, 
  TrendingUp, Activity, Zap 
} from 'lucide-react';
import { useStatsEngine } from '@/hooks/useStatsEngine';

/**
 * StatBlock - Bloc individuel de statistique
 */
export function StatBlock({ 
  value, 
  label, 
  icon: Icon = Activity,
  color = "text-[#f5a623]",
  delay = 0,
  showTrend = false,
  trendUp = true 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="relative group"
    >
      <div className="bg-black/60 backdrop-blur-sm border border-white/10 rounded-sm p-6 
                      hover:border-[#f5a623]/30 transition-all duration-300
                      hover:shadow-lg hover:shadow-[#f5a623]/5">
        {/* Icon */}
        <div className={`inline-flex items-center justify-center w-10 h-10 rounded-sm 
                        bg-white/5 ${color} mb-4 group-hover:scale-110 transition-transform`}>
          <Icon className="h-5 w-5" />
        </div>
        
        {/* Value */}
        <div className="flex items-baseline gap-2">
          <span className="font-barlow text-3xl md:text-4xl font-bold text-white tracking-tight">
            {value}
          </span>
          {showTrend && (
            <TrendingUp className={`h-4 w-4 ${trendUp ? 'text-green-400' : 'text-red-400'}`} />
          )}
        </div>
        
        {/* Label */}
        <p className="text-gray-300 text-xs uppercase tracking-widest mt-2 font-medium">
          {label}
        </p>
        
        {/* Decorative accent line */}
        <div className={`absolute bottom-0 left-0 h-0.5 w-0 group-hover:w-full 
                        ${color.replace('text-', 'bg-')} transition-all duration-500`} />
      </div>
    </motion.div>
  );
}

/**
 * StatsPanel - Grille complète des statistiques BIONIC™
 */
export function StatsPanel({ className = "" }) {
  const stats = useStatsEngine({});

  const statsConfig = [
    {
      value: stats.displayedSubscribers,
      label: "Membres Abonnés",
      icon: Users,
      color: "text-emerald-400",
      delay: 0,
    },
    {
      value: stats.displayedTerritories,
      label: "Territoires Analysés",
      icon: MapPin,
      color: "text-blue-400",
      delay: 0.1,
    },
    {
      value: "850+",
      label: "Attractants Testés",
      icon: Beaker,
      color: "text-purple-400",
      delay: 0.2,
    },
    {
      value: stats.displayedZones,
      label: "Zones de Chasse",
      icon: Target,
      color: "text-[#f5a623]",
      delay: 0.3,
    },
    {
      value: `${stats.satisfaction}%`,
      label: "Satisfaction",
      icon: ThumbsUp,
      color: "text-green-400",
      delay: 0.4,
      showTrend: true,
      trendUp: true,
    },
  ];

  return (
    <section 
      className={`py-16 bg-gradient-to-b from-[#0a0a0a] to-[#0d1117] ${className}`}
      data-testid="stats-panel"
    >
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#f5a623]/10 
                          border border-[#f5a623]/20 rounded-full mb-4">
            <Zap className="h-4 w-4 text-[#f5a623]" />
            <span className="text-[#f5a623] text-sm font-medium">BIONIC™ Stats Engine</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white font-barlow mb-3">
            La Communauté BIONIC HUNT/Chasse
          </h2>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Des milliers de chasseurs font confiance à notre technologie BIONIC™ 
            pour optimiser leurs sorties de chasse.
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 md:gap-6">
          {statsConfig.map((stat, index) => (
            <StatBlock
              key={index}
              value={stat.value}
              label={stat.label}
              icon={stat.icon}
              color={stat.color}
              delay={stat.delay}
              showTrend={stat.showTrend}
              trendUp={stat.trendUp}
            />
          ))}
        </div>

        {/* Bottom decoration */}
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-12 h-px bg-gradient-to-r from-transparent via-[#f5a623]/30 to-transparent"
        />
      </div>
    </section>
  );
}

/**
 * CompactStatsBar - Version compacte pour header/footer
 */
export function CompactStatsBar({ className = "" }) {
  const stats = useStatsEngine({ refreshInterval: 30000 });

  return (
    <div className={`flex items-center justify-center gap-8 py-3 
                    bg-black/40 border-y border-white/5 ${className}`}>
      {[
        { value: stats.displayedSubscribers, label: "Membres" },
        { value: stats.displayedTerritories, label: "Territoires" },
        { value: stats.displayedZones, label: "Zones" },
      ].map((item, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span className="font-bold text-white">{item.value}</span>
          <span className="text-gray-500">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

export default {
  StatsPanel,
  StatBlock,
  CompactStatsBar,
  useStatsEngine,
};
