/**
 * BIONIC DESIGN SYSTEM - Icons Configuration
 * Mapping centralisé des icônes (remplace tous les emojis)
 * Version: 1.0.0
 * 
 * RÈGLES:
 * - Utiliser UNIQUEMENT les icônes Lucide React
 * - Aucun emoji autorisé dans le code
 * - Importer ce fichier pour tous les mappings d'icônes
 */

import {
  Target,
  BarChart3,
  TrendingUp,
  Cloud,
  Sun,
  Moon,
  Wind,
  MapPin,
  Flame,
  FlaskConical,
  Bot,
  Droplet,
  TreePine,
  Timer,
  Camera,
  Eye,
  Trophy,
  Crosshair,
  Navigation,
  Compass,
  Mountain,
  Home,
  Building,
  Lock,
  Tent,
  Car,
  CircleDot,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Loader2,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Menu,
  X,
  Search,
  Filter,
  Download,
  Upload,
  Share,
  Copy,
  Edit,
  Trash2,
  Plus,
  Minus,
  Settings,
  User,
  Users,
  Calendar,
  Clock,
  Thermometer,
  Gauge,
  Activity,
  Heart,
  Star,
  Bookmark,
  Bell,
  Mail,
  Phone,
  Globe,
  Map,
  Layers,
  Grid,
  List,
  LayoutGrid,
  FileText,
  FolderOpen,
  Package,
  ShoppingCart,
  CreditCard,
  DollarSign,
  Percent,
  BarChart,
  PieChart,
  LineChart,
  Zap,
  Shield,
  Award,
  Gift,
  Send,
  MessageSquare,
  HelpCircle,
  ExternalLink,
  Link,
  Unlink,
  RefreshCw,
  RotateCcw,
  Save,
  LogOut,
  LogIn,
  Maximize,
  Minimize,
  ZoomIn,
  ZoomOut,
  Move,
  Grip,
  MoreHorizontal,
  MoreVertical,
  Sunrise,
  Sunset,
  CloudRain,
  CloudSnow,
  CloudFog,
  Waves,
  Beef,
  Gem,
  Hash,
  Radar,
  Scan,
  ScanLine,
  Focus,
  Sparkles,
  Binoculars,
  Route,
  Footprints,
  TreeDeciduous,
  Leaf,
  Sprout
} from 'lucide-react';

/**
 * Mapping des icônes par catégorie
 * Utiliser ces références dans tous les composants
 */

// ============================================
// ICÔNES GÉNÉRALES
// ============================================

export const BIONIC_ICONS = {
  // Navigation & Actions
  target: Target,
  menu: Menu,
  close: X,
  search: Search,
  filter: Filter,
  settings: Settings,
  more: MoreHorizontal,
  moreVertical: MoreVertical,
  chevronRight: ChevronRight,
  chevronDown: ChevronDown,
  chevronUp: ChevronUp,
  externalLink: ExternalLink,
  
  // CRUD
  add: Plus,
  remove: Minus,
  edit: Edit,
  delete: Trash2,
  save: Save,
  download: Download,
  upload: Upload,
  share: Share,
  copy: Copy,
  refresh: RefreshCw,
  undo: RotateCcw,
  
  // Status
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  loading: Loader2,
  
  // Auth
  login: LogIn,
  logout: LogOut,
  user: User,
  users: Users,
  lock: Lock,
  
  // Data & Analytics
  chart: BarChart3,
  pieChart: PieChart,
  lineChart: LineChart,
  barChart: BarChart,
  trending: TrendingUp,
  activity: Activity,
  gauge: Gauge,
  
  // Communication
  bell: Bell,
  mail: Mail,
  phone: Phone,
  message: MessageSquare,
  send: Send,
  help: HelpCircle,
};

// ============================================
// ICÔNES MÉTÉO (remplace les emojis météo)
// ============================================

export const WEATHER_ICONS = {
  clear: Sun,
  sunny: Sun,
  cloudy: Cloud,
  partly_cloudy: Cloud, // Utiliser avec opacité différente
  rain: CloudRain,
  snow: CloudSnow,
  fog: CloudFog,
  wind: Wind,
  storm: Zap,
  sunrise: Sunrise,
  sunset: Sunset,
  moon: Moon,
  temperature: Thermometer,
};

// ============================================
// ICÔNES TERRITOIRE & WAYPOINTS
// ============================================

export const TERRITORY_ICONS = {
  // Types de waypoints
  hunting: Target,
  camera: Camera,
  feeding: Sprout,
  observation: Eye,
  blind: Crosshair,
  custom: MapPin,
  
  // Types de lieux
  zec: Tent,
  pourvoirie: Home,
  private: Lock,
  reserve: Shield,
  stand: Target,
  salt_lick: Droplet,
  observation_point: Binoculars,
  parking: Car,
  camp: Tent,
  other: MapPin,
  
  // Navigation
  gps: Navigation,
  compass: Compass,
  route: Route,
  footprints: Footprints,
  
  // Terrain
  mountain: Mountain,
  forest: TreePine,
  tree: TreeDeciduous,
  water: Waves,
  
  // Zones
  hotspot: Flame,
  standard: CircleDot,
  weak: AlertTriangle,
};

// ============================================
// ICÔNES ANIMAUX (remplace les emojis animaux)
// Note: Pour les animaux, utiliser des images réelles
// Ces icônes sont des placeholders tactiques
// ============================================

export const ANIMAL_ICONS = {
  deer: CircleDot,      // Placeholder - utiliser image réelle
  moose: CircleDot,     // Placeholder - utiliser image réelle
  bear: CircleDot,      // Placeholder - utiliser image réelle
  wild_boar: CircleDot, // Placeholder - utiliser image réelle
  turkey: CircleDot,    // Placeholder - utiliser image réelle
  duck: CircleDot,      // Placeholder - utiliser image réelle
  coyote: CircleDot,    // Placeholder - utiliser image réelle
  fox: CircleDot,       // Placeholder - utiliser image réelle
  default: Target,
};

// ============================================
// ICÔNES NUTRITION & ANALYSE
// ============================================

export const NUTRITION_ICONS = {
  proteins: Beef,
  minerals: Gem,
  attractiveness: Target,
  duration: Timer,
  analysis: FlaskConical,
  score: BarChart3,
};

// ============================================
// ICÔNES AI & INSIGHTS
// ============================================

export const AI_ICONS = {
  bot: Bot,
  insight: Sparkles,
  tip: Zap,
  trend: TrendingUp,
  warning: AlertTriangle,
  recommendation: Target,
  strategy: Radar,
};

// ============================================
// ICÔNES COMMERCE
// ============================================

export const COMMERCE_ICONS = {
  cart: ShoppingCart,
  package: Package,
  dollar: DollarSign,
  percent: Percent,
  card: CreditCard,
  star: Star,
  award: Award,
  gift: Gift,
};

// ============================================
// MAPPING EMOJI → ICÔNE
// Utiliser pour la migration des anciens composants
// ============================================

export const EMOJI_TO_ICON_MAP = {
  // Général
  '🎯': Target,
  '📊': BarChart3,
  '📈': TrendingUp,
  '🔥': Flame,
  '⚡': Zap,
  '💡': Sparkles,
  '🧪': FlaskConical,
  '🤖': Bot,
  '⏱️': Timer,
  '🏆': Trophy,
  '⭐': Star,
  '📍': MapPin,
  '🔒': Lock,
  '👁️': Eye,
  '📷': Camera,
  '💧': Droplet,
  '💎': Gem,
  '🥩': Beef,
  '🌲': TreePine,
  '🌿': Leaf,
  
  // Météo
  '☀️': Sun,
  '🌤️': Cloud,
  '⛅': Cloud,
  '🌧️': CloudRain,
  '❄️': CloudSnow,
  '🌙': Moon,
  '💨': Wind,
  '🌡️': Thermometer,
  '🌇': Sunset,
  
  // Territoire
  '🏕️': Tent,
  '🏠': Home,
  '🏡': Building,
  '🧂': Droplet,
  '🅿️': Car,
  '📌': MapPin,
  '🗺️': Map,
  
  // Animaux (placeholder - utiliser images réelles)
  '🦌': CircleDot,
  '🫎': CircleDot,
  '🐻': CircleDot,
  '🐗': CircleDot,
  '🦃': CircleDot,
  '🦆': CircleDot,
  '🦊': CircleDot,
  
  // Status
  '✅': CheckCircle,
  '✓': CheckCircle,
  '✕': XCircle,
  '✗': XCircle,
  '⚠️': AlertTriangle,
  
  // Actions
  '💾': Save,
  '🗑️': Trash2,
  '📥': Download,
  '📄': FileText,
  '📋': FileText,
  '📜': FileText,
  '🥧': PieChart,
};

/**
 * Fonction utilitaire pour obtenir l'icône correspondante à un emoji
 * @param {string} emoji - L'emoji à convertir
 * @returns {Component} - Le composant Lucide correspondant
 */
export const getIconForEmoji = (emoji) => {
  return EMOJI_TO_ICON_MAP[emoji] || CircleDot;
};

/**
 * Fonction utilitaire pour obtenir l'icône météo
 * @param {string} condition - La condition météo
 * @returns {Component} - Le composant Lucide correspondant
 */
export const getWeatherIcon = (condition) => {
  const normalizedCondition = condition?.toLowerCase().replace(/\s+/g, '_');
  return WEATHER_ICONS[normalizedCondition] || Cloud;
};

/**
 * Fonction utilitaire pour obtenir l'icône de waypoint
 * @param {string} type - Le type de waypoint
 * @returns {Component} - Le composant Lucide correspondant
 */
export const getWaypointIcon = (type) => {
  return TERRITORY_ICONS[type] || MapPin;
};

/**
 * Fonction utilitaire pour obtenir l'icône de lieu
 * @param {string} type - Le type de lieu
 * @returns {Component} - Le composant Lucide correspondant
 */
export const getPlaceIcon = (type) => {
  return TERRITORY_ICONS[type] || MapPin;
};

export default BIONIC_ICONS;
