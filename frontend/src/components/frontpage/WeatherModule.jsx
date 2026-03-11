import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Cloud, Sun, CloudRain, Wind, Thermometer, Droplets, 
  Eye, Gauge, Sunrise, Sunset, Moon, TrendingUp, TrendingDown,
  CloudSnow, CloudFog, Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { WeatherService } from '@/services';

const WeatherModule = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch weather data from service
  useEffect(() => {
    const fetchWeather = async () => {
      setLoading(true);
      try {
        const data = await WeatherService.getRegionWeather('laurentides');
        // Transform data for component
        setWeather({
          location: `${data.location}, QC`,
          current: {
            temp: data.temp,
            feels_like: data.feels_like,
            humidity: data.humidity,
            pressure: data.pressure,
            wind_speed: data.wind_speed,
            wind_dir: data.wind_dir,
            visibility: data.visibility,
            condition: data.condition,
            icon: data.icon
          },
          hunting: data.hunting,
          sunrise: data.sunrise || '07:15',
          sunset: data.sunset || '16:45',
          moon_phase: data.moon_phase || 'Croissant',
          forecast: data.forecast || []
        });
      } catch (err) {
        console.error('Weather fetch error:', err);
        // Fallback to simulated data
        const fallback = WeatherService.getSimulatedWeather('Laurentides');
        setWeather({
          location: `${fallback.location}, QC`,
          current: {
            temp: fallback.temp,
            feels_like: fallback.feels_like,
            humidity: fallback.humidity,
            pressure: fallback.pressure,
            wind_speed: fallback.wind_speed,
            wind_dir: fallback.wind_dir,
            visibility: fallback.visibility,
            condition: fallback.condition,
            icon: fallback.icon
          },
          hunting: fallback.hunting,
          sunrise: fallback.sunrise,
          sunset: fallback.sunset,
          moon_phase: fallback.moon_phase,
          forecast: fallback.forecast
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchWeather();
  }, []);

  const getWeatherIcon = (icon) => {
    const icons = {
      'sun': Sun,
      'cloud': Cloud,
      'cloud-sun': Cloud,
      'cloud-rain': CloudRain,
      'cloud-snow': CloudSnow,
      'fog': CloudFog,
      'storm': Zap
    };
    return icons[icon] || Cloud;
  };

  if (loading) {
    return (
      <section className="py-16 px-4 bg-[#0a0a0a]">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-64 bg-white/5 rounded-md" />
            <div className="h-64 bg-white/5 rounded-md" />
            <div className="h-64 bg-white/5 rounded-md" />
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 px-4 bg-[#0a0a0a]" data-testid="weather-module-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center gap-3 mb-8">
          <Cloud className="h-6 w-6 text-[#f5a623]" />
          <div>
            <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold block">Météo & Conditions</span>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Conditions <span className="text-[#f5a623]">optimales</span>
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Weather Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-2"
          >
            <Card className="bg-gradient-to-br from-[#1a1a1a] to-[#0d1117] border-white/5 rounded-md overflow-hidden h-full">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <p className="text-gray-300 text-sm">{weather.location}</p>
                    <div className="flex items-end gap-2 mt-1">
                      <span className="font-barlow text-6xl font-bold text-white">{weather.current.temp}°</span>
                      <span className="text-gray-300 text-lg mb-2">Ressenti {weather.current.feels_like}°</span>
                    </div>
                    <p className="text-gray-300 mt-2">{weather.current.condition}</p>
                  </div>
                  <div className="text-right">
                    {(() => {
                      const WeatherIcon = getWeatherIcon(weather.current.icon);
                      return <WeatherIcon className="h-16 w-16 text-[#f5a623]" />;
                    })()}
                  </div>
                </div>

                {/* Weather Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
                  <div className="text-center">
                    <Wind className="h-5 w-5 text-[#f5a623] mx-auto mb-1" />
                    <p className="text-white font-semibold">{weather.current.wind_speed} km/h</p>
                    <p className="text-gray-300 text-xs">Vent {weather.current.wind_dir}</p>
                  </div>
                  <div className="text-center">
                    <Droplets className="h-5 w-5 text-blue-400 mx-auto mb-1" />
                    <p className="text-white font-semibold">{weather.current.humidity}%</p>
                    <p className="text-gray-300 text-xs">Humidité</p>
                  </div>
                  <div className="text-center">
                    <Gauge className="h-5 w-5 text-purple-400 mx-auto mb-1" />
                    <p className="text-white font-semibold">{weather.current.pressure} hPa</p>
                    <p className="text-gray-300 text-xs">Pression</p>
                  </div>
                  <div className="text-center">
                    <Eye className="h-5 w-5 text-green-400 mx-auto mb-1" />
                    <p className="text-white font-semibold">{weather.current.visibility} km</p>
                    <p className="text-gray-300 text-xs">Visibilité</p>
                  </div>
                </div>

                {/* Sun/Moon Times */}
                <div className="flex items-center justify-center gap-8 mt-6 pt-6 border-t border-white/10">
                  <div className="flex items-center gap-2">
                    <Sunrise className="h-5 w-5 text-orange-400" />
                    <span className="text-white">{weather.sunrise}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Sunset className="h-5 w-5 text-orange-600" />
                    <span className="text-white">{weather.sunset}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Moon className="h-5 w-5 text-blue-300" />
                    <span className="text-white">{weather.moon_phase}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Hunting Score Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            viewport={{ once: true }}
          >
            <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden h-full">
              <CardContent className="p-6 flex flex-col h-full">
                <div className="text-center mb-6">
                  <p className="text-gray-300 text-sm uppercase tracking-wider mb-2">Score de chasse</p>
                  <div className="relative inline-flex items-center justify-center">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="transparent"
                        className="text-white/10"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="transparent"
                        strokeDasharray={`${(weather.hunting.score / 100) * 352} 352`}
                        className="text-[#f5a623]"
                      />
                    </svg>
                    <span className="absolute font-barlow text-4xl font-bold text-white">
                      {weather.hunting.score}
                    </span>
                  </div>
                  <Badge className="mt-4 bg-green-500/20 text-green-400 border-green-500/30">
                    {weather.hunting.status}
                  </Badge>
                </div>

                <div className="flex-1">
                  <p className="text-gray-300 text-sm text-center">{weather.hunting.advice}</p>
                </div>

                {/* 5-Day Forecast */}
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-gray-300 text-xs uppercase tracking-wider mb-3">Prévisions 5 jours</p>
                  <div className="flex justify-between">
                    {weather.forecast.map((day, i) => {
                      const ForecastIcon = getWeatherIcon(day.icon);
                      return (
                        <div key={i} className="text-center">
                          <p className="text-gray-300 text-xs">{day.day}</p>
                          <ForecastIcon className="h-4 w-4 text-white/60 mx-auto my-1" />
                          <p className="text-white text-xs">{day.temp_high}°</p>
                          <p className="text-gray-500 text-xs">{day.temp_low}°</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default WeatherModule;
