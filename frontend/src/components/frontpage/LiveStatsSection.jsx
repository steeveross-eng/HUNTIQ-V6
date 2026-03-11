import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, TrendingUp, TrendingDown, Users, ShoppingCart, 
  MapPin, Eye, Zap, ArrowUp, ArrowDown, BarChart3, Bell,
  AlertTriangle, Info, CheckCircle, Clock
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LiveStatsSection = () => {
  const [stats, setStats] = useState({
    activeUsers: 1247,
    todaySales: 34,
    activeZones: 29,
    alertsToday: 12
  });
  const [ticker, setTicker] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // Simulated live ticker data
    const tickerData = [
      { type: 'sale', message: 'Nouveau achat: Buck Bomb Deer Lure', zone: 'Laurentides', time: '2 min' },
      { type: 'activity', message: 'Activité intense détectée', zone: 'Zone 17', time: '5 min' },
      { type: 'weather', message: 'Pression en hausse +5 hPa', zone: 'Abitibi', time: '8 min' },
      { type: 'user', message: 'Nouvelle inscription', zone: 'Montréal', time: '12 min' },
      { type: 'territory', message: 'Territoire ajouté aux favoris', zone: 'Saguenay', time: '15 min' },
    ];

    const alertsData = [
      { id: 1, type: 'warning', title: 'Zone de chasse fermée', message: 'Zone 8 fermée jusqu\'au 15 décembre', time: 'Maintenant' },
      { id: 2, type: 'info', title: 'Nouveau règlement', message: 'Limite de prises mise à jour pour Zone 14', time: '1h' },
      { id: 3, type: 'success', title: 'Conditions optimales', message: 'Pression stable dans la région des Laurentides', time: '2h' },
    ];

    setTicker(tickerData);
    setAlerts(alertsData);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setStats(prev => ({
        activeUsers: prev.activeUsers + Math.floor(Math.random() * 10) - 5,
        todaySales: prev.todaySales + (Math.random() > 0.7 ? 1 : 0),
        activeZones: 29,
        alertsToday: prev.alertsToday + (Math.random() > 0.9 ? 1 : 0)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getAlertIcon = (type) => {
    switch(type) {
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'info': return <Info className="h-4 w-4 text-blue-400" />;
      case 'success': return <CheckCircle className="h-4 w-4 text-green-400" />;
      default: return <Bell className="h-4 w-4 text-gray-300" />;
    }
  };

  const getTickerIcon = (type) => {
    switch(type) {
      case 'sale': return <ShoppingCart className="h-4 w-4 text-green-400" />;
      case 'activity': return <Zap className="h-4 w-4 text-[#f5a623]" />;
      case 'weather': return <TrendingUp className="h-4 w-4 text-blue-400" />;
      case 'user': return <Users className="h-4 w-4 text-purple-400" />;
      case 'territory': return <MapPin className="h-4 w-4 text-red-400" />;
      default: return <Activity className="h-4 w-4 text-gray-300" />;
    }
  };

  return (
    <section className="py-8 bg-[#0d1117] border-y border-white/5" data-testid="live-stats-section">
      <div className="max-w-7xl mx-auto px-4">
        {/* Live Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Utilisateurs actifs', value: stats.activeUsers, icon: Users, trend: 'up', color: 'text-green-400' },
            { label: 'Ventes aujourd\'hui', value: stats.todaySales, icon: ShoppingCart, trend: 'up', color: 'text-[#f5a623]' },
            { label: 'Zones actives', value: stats.activeZones, icon: MapPin, trend: 'stable', color: 'text-blue-400' },
            { label: 'Alertes', value: stats.alertsToday, icon: Bell, trend: 'up', color: 'text-red-400' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="bg-black/40 backdrop-blur-sm border-white/5 rounded-sm">
                <CardContent className="p-4 flex items-center gap-4">
                  <div className={`p-2 rounded-sm bg-white/5 ${stat.color}`}>
                    <stat.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-barlow text-2xl font-bold text-white">{stat.value.toLocaleString()}</span>
                      {stat.trend === 'up' && <ArrowUp className="h-4 w-4 text-green-400" />}
                      {stat.trend === 'down' && <ArrowDown className="h-4 w-4 text-red-400" />}
                    </div>
                    <p className="text-gray-300 text-xs uppercase tracking-wider">{stat.label}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Live Ticker */}
        <div className="flex items-center gap-4 overflow-hidden py-3 border-t border-b border-white/5">
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-red-500 font-mono text-sm font-bold">LIVE</span>
          </div>
          
          <div className="flex-1 overflow-hidden">
            <motion.div 
              className="flex gap-8"
              animate={{ x: [0, -1000] }}
              transition={{ 
                duration: 30, 
                repeat: Infinity, 
                ease: 'linear' 
              }}
            >
              {[...ticker, ...ticker].map((item, i) => (
                <div key={i} className="flex items-center gap-3 flex-shrink-0">
                  {getTickerIcon(item.type)}
                  <span className="text-white text-sm">{item.message}</span>
                  <Badge className="bg-white/10 text-gray-300 text-xs">{item.zone}</Badge>
                  <span className="text-gray-500 text-xs">{item.time}</span>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Alerts Section */}
        <div className="mt-6">
          <div className="flex items-center gap-2 mb-4">
            <Bell className="h-5 w-5 text-[#f5a623]" />
            <span className="text-white font-semibold">Alertes & Notifications</span>
            <Badge className="bg-red-500/20 text-red-400 text-xs">{alerts.length} nouvelles</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {alerts.map((alert, i) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className="bg-black/40 backdrop-blur-sm border-white/5 rounded-sm hover:border-white/10 transition-colors cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {getAlertIcon(alert.type)}
                      <div className="flex-1">
                        <h4 className="text-white font-medium text-sm">{alert.title}</h4>
                        <p className="text-gray-300 text-xs mt-1">{alert.message}</p>
                        <div className="flex items-center gap-1 mt-2 text-gray-500 text-xs">
                          <Clock className="h-3 w-3" />
                          {alert.time}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default LiveStatsSection;
