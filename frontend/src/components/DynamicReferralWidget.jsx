// DynamicReferralWidget.jsx - Widget flottant dynamique et responsive
import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { 
  Gift,
  Share2,
  Copy,
  Check,
  X,
  Users,
  DollarSign,
  Percent,
  ChevronUp,
  ChevronDown,
  Crown,
  Sparkles,
  Trophy,
  ArrowRight,
  UserPlus,
  Zap,
  TrendingUp,
  Loader2
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Logo URLs for different contexts
const LOGOS = {
  main: "https://customer-assets.emergentagent.com/job_bait-analyzer-pro/artifacts/aux7tlxe_Scent%20sciences%20Laboratory%20LOGO.png",
  mini: "https://customer-assets.emergentagent.com/job_bait-analyzer-pro/artifacts/aux7tlxe_Scent%20sciences%20Laboratory%20LOGO.png"
};

// Page-specific theme configurations
const PAGE_THEMES = {
  "/": {
    name: "home",
    primary: "#f5a623",
    secondary: "#d4850e",
    accent: "#f7c857",
    gradient: "from-[#f5a623] to-[#d4850e]",
    bgCard: "bg-black/90",
    textPrimary: "text-white",
    textSecondary: "text-gray-300"
  },
  "/analyze": {
    name: "analyze",
    primary: "#f5a623",
    secondary: "#d4850e",
    accent: "#f7c857",
    gradient: "from-[#f5a623] to-[#d4850e]",
    bgCard: "bg-black/90",
    textPrimary: "text-white",
    textSecondary: "text-gray-300"
  },
  "/compare": {
    name: "compare",
    primary: "#8b5cf6",
    secondary: "#7c3aed",
    accent: "#a78bfa",
    gradient: "from-violet-500 to-violet-700",
    bgCard: "bg-violet-950/90",
    textPrimary: "text-white",
    textSecondary: "text-violet-200"
  },
  "/shop": {
    name: "shop",
    primary: "#f5a623",
    secondary: "#d4850e",
    accent: "#f7c857",
    gradient: "from-[#f5a623] to-[#d4850e]",
    bgCard: "bg-black/90",
    textPrimary: "text-white",
    textSecondary: "text-gray-300"
  },
  "/referral": {
    name: "referral",
    primary: "#f5a623",
    secondary: "#d4850e",
    accent: "#f7c857",
    gradient: "from-[#f5a623] to-[#d4850e]",
    bgCard: "bg-black/90",
    textPrimary: "text-white",
    textSecondary: "text-gray-300"
  }
};

// Tier configurations with enhanced visuals
const TIER_CONFIG = {
  bronze: { 
    color: "from-amber-700 to-amber-900", 
    icon: "🥉", 
    label: "Bronze", 
    next: "silver",
    glowColor: "shadow-amber-500/30"
  },
  silver: { 
    color: "from-gray-400 to-gray-600", 
    icon: "🥈", 
    label: "Argent", 
    next: "gold",
    glowColor: "shadow-gray-400/30"
  },
  gold: { 
    color: "from-yellow-500 to-yellow-700", 
    icon: "🥇", 
    label: "Or", 
    next: "platinum",
    glowColor: "shadow-yellow-500/40"
  },
  platinum: { 
    color: "from-cyan-400 to-cyan-600", 
    icon: "💎", 
    label: "Platine", 
    next: "diamond",
    glowColor: "shadow-cyan-400/40"
  },
  diamond: { 
    color: "from-purple-500 to-purple-700", 
    icon: "👑", 
    label: "Diamant", 
    next: null,
    glowColor: "shadow-purple-500/50"
  },
  partner: { 
    color: "from-[#f5a623] to-purple-600", 
    icon: "⭐", 
    label: "Partenaire", 
    next: null,
    glowColor: "shadow-[#f5a623]/50"
  }
};

// Share platforms
const SHARE_PLATFORMS = [
  { id: "facebook", icon: "📘", color: "bg-[#1877F2]", label: "Facebook" },
  { id: "whatsapp", icon: "💬", color: "bg-[#25D366]", label: "WhatsApp" },
  { id: "instagram", icon: "📷", color: "bg-gradient-to-r from-[#833AB4] via-[#E1306C] to-[#F77737]", label: "Instagram" },
  { id: "sms", icon: "📱", color: "bg-[#34C759]", label: "SMS" },
  { id: "email", icon: "📧", color: "bg-[#EA4335]", label: "Email" },
  { id: "copy", icon: "📋", color: "bg-gray-600", label: "Copier" }
];

// Animated counter component
const AnimatedCounter = ({ value, prefix = "", suffix = "", className = "", duration = 1000, style = {} }) => {
  const [displayValue, setDisplayValue] = useState(value);
  const [isAnimating, setIsAnimating] = useState(false);
  const prevValueRef = useRef(value);
  const isFirstRender = useRef(true);

  useEffect(() => {
    // On first render, set the value directly
    if (isFirstRender.current) {
      setDisplayValue(value);
      prevValueRef.current = value;
      isFirstRender.current = false;
      return;
    }
    
    // On subsequent updates, animate if value changed
    if (prevValueRef.current !== value) {
      setIsAnimating(true);
      const startValue = prevValueRef.current;
      const endValue = value;
      const startTime = Date.now();
      
      const animate = () => {
        const now = Date.now();
        const progress = Math.min((now - startTime) / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = startValue + (endValue - startValue) * easeOutQuart;
        
        setDisplayValue(Math.round(currentValue * 100) / 100);
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setDisplayValue(endValue);
          setIsAnimating(false);
        }
      };
      
      requestAnimationFrame(animate);
      prevValueRef.current = value;
    }
  }, [value, duration]);

  return (
    <span className={`${className} ${isAnimating ? 'scale-110 transition-transform' : 'transition-transform'}`} style={style}>
      {prefix}{typeof displayValue === 'number' && displayValue % 1 !== 0 ? displayValue.toFixed(2) : displayValue}{suffix}
    </span>
  );
};

// Pulsing reward indicator
const RewardPulse = ({ active, children }) => {
  if (!active) return children;
  
  return (
    <div className="relative">
      <span className="absolute inset-0 animate-ping rounded-full bg-[#f5a623] opacity-30" />
      <span className="absolute inset-0 animate-pulse rounded-full bg-[#f5a623] opacity-20" />
      {children}
    </div>
  );
};

const DynamicReferralWidget = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const [registerForm, setRegisterForm] = useState({ name: "", email: "" });
  const [registering, setRegistering] = useState(false);
  
  // Animation states
  const [animateReward, setAnimateReward] = useState(false);
  const [recentRewardGain, setRecentRewardGain] = useState(null);
  
  // Theme state based on current page
  const [currentTheme, setCurrentTheme] = useState(PAGE_THEMES["/"]);
  const [currentPath, setCurrentPath] = useState("/");
  
  // Real-time sync interval
  const syncIntervalRef = useRef(null);
  const previousUserDataRef = useRef(null);

  // Update theme based on current path
  useEffect(() => {
    const updateTheme = () => {
      const path = window.location.pathname;
      setCurrentPath(path);
      
      // Find matching theme or use default
      const matchedTheme = PAGE_THEMES[path] || PAGE_THEMES["/"];
      setCurrentTheme(matchedTheme);
    };
    
    updateTheme();
    
    // Listen for route changes (for SPA navigation)
    const handleRouteChange = () => {
      updateTheme();
    };
    
    window.addEventListener('popstate', handleRouteChange);
    
    // Use MutationObserver to detect React Router changes
    const observer = new MutationObserver(() => {
      if (window.location.pathname !== currentPath) {
        updateTheme();
      }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
      observer.disconnect();
    };
  }, [currentPath]);

  // Load user data
  const loadUserData = useCallback(async (showAnimation = false) => {
    const savedUserId = localStorage.getItem("referral_user_id");
    const savedEmail = localStorage.getItem("user_email");
    
    if (savedUserId) {
      try {
        const response = await axios.get(`${API}/referral/dashboard/${savedUserId}`);
        const newUserData = response.data.user;
        
        // Check for reward changes
        if (previousUserDataRef.current && showAnimation) {
          const prevDiscount = previousUserDataRef.current.current_discount_percent;
          const newDiscount = newUserData.current_discount_percent;
          
          if (newDiscount > prevDiscount) {
            setAnimateReward(true);
            setRecentRewardGain(newDiscount - prevDiscount);
            setTimeout(() => {
              setAnimateReward(false);
              setRecentRewardGain(null);
            }, 3000);
          }
        }
        
        previousUserDataRef.current = newUserData;
        setUser(newUserData);
      } catch (error) {
        localStorage.removeItem("referral_user_id");
      }
    } else if (savedEmail) {
      try {
        const response = await axios.get(`${API}/referral/user/${encodeURIComponent(savedEmail)}`);
        setUser(response.data);
        localStorage.setItem("referral_user_id", response.data.id);
        previousUserDataRef.current = response.data;
      } catch (error) {
        // User doesn't have a referral account yet
      }
    }
    setLoading(false);
  }, []);

  // Initial load and real-time sync setup
  useEffect(() => {
    loadUserData();
    
    // Set up real-time sync every 30 seconds
    syncIntervalRef.current = setInterval(() => {
      loadUserData(true);
    }, 30000);
    
    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [loadUserData]);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!registerForm.name || !registerForm.email) {
      toast.error("Veuillez remplir tous les champs");
      return;
    }
    
    setRegistering(true);
    try {
      const response = await axios.post(`${API}/referral/register`, registerForm);
      localStorage.setItem("referral_user_id", response.data.user.id);
      localStorage.setItem("referral_code", response.data.referral_code);
      setUser(response.data.user);
      previousUserDataRef.current = response.data.user;
      setShowRegistration(false);
      setAnimateReward(true);
      setTimeout(() => setAnimateReward(false), 3000);
      toast.success("Bienvenue dans le programme de parrainage!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de l'inscription");
    }
    setRegistering(false);
  };

  const copyLink = () => {
    if (!user?.referral_link) return;
    navigator.clipboard.writeText(user.referral_link);
    setCopied(true);
    toast.success("Lien copié!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = (platformId) => {
    if (!user?.referral_link) return;
    
    const message = `Découvrez SCENT SCIENCE - L'analyse scientifique des attractants de chasse! Utilisez mon lien pour ${user.current_discount_percent}% de rabais!`;
    const link = user.referral_link;
    
    const shareUrls = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(link)}&quote=${encodeURIComponent(message)}`,
      whatsapp: `https://api.whatsapp.com/send?text=${encodeURIComponent(message + " " + link)}`,
      sms: `sms:?body=${encodeURIComponent(message + " " + link)}`,
      email: `mailto:?subject=${encodeURIComponent("Découvrez SCENT SCIENCE™!")}&body=${encodeURIComponent(message + "\n\n" + link)}`
    };

    if (platformId === "copy") {
      copyLink();
      return;
    }

    if (platformId === "instagram") {
      navigator.clipboard.writeText(message + "\n\n" + link);
      toast.success("Message copié! Collez-le dans Instagram");
      return;
    }

    if (shareUrls[platformId]) {
      window.open(shareUrls[platformId], "_blank", "width=600,height=400");
    }
  };

  const tierConfig = user ? TIER_CONFIG[user.tier] || TIER_CONFIG.bronze : TIER_CONFIG.bronze;
  const nextTierConfig = tierConfig.next ? TIER_CONFIG[tierConfig.next] : null;

  // Don't show on admin page
  if (typeof window !== 'undefined' && window.location.pathname.startsWith("/admin")) {
    return null;
  }

  // Generate theme-aware styles
  const getButtonStyle = () => {
    if (user) {
      return `bg-gradient-to-r ${tierConfig.color}`;
    }
    return `bg-gradient-to-r ${currentTheme.gradient}`;
  };

  return (
    <>
      {/* Floating Widget Container - positioned above the Emergent badge */}
      <div 
        className="fixed bottom-20 right-4 sm:bottom-24 sm:right-6 z-50 flex flex-col items-end gap-2"
        data-testid="dynamic-referral-widget"
      >
        {/* Reward gain notification */}
        {recentRewardGain && (
          <div className="animate-bounce bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
            +{recentRewardGain}%
          </div>
        )}
        
        {/* Expanded Quick Stats Panel */}
        {isExpanded && user && (
          <div 
            className={`${currentTheme.bgCard} backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl animate-in slide-in-from-bottom-2 duration-300 w-[280px] sm:w-80`}
            style={{
              boxShadow: `0 25px 50px -12px ${currentTheme.primary}40`
            }}
          >
            {/* Header with logo and user info */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <img 
                    src={LOGOS.mini} 
                    alt="SCENT SCIENCE™" 
                    className="h-10 w-10 rounded-full object-contain bg-black/50 p-1 ring-2"
                    style={{ ringColor: currentTheme.primary }}
                  />
                  <span className="absolute -bottom-1 -right-1 text-lg">{tierConfig.icon}</span>
                </div>
                <div>
                  <p className={`${currentTheme.textPrimary} font-semibold text-sm`}>{user.name}</p>
                  <Badge 
                    className={`bg-gradient-to-r ${tierConfig.color} text-white text-xs px-2`}
                  >
                    {tierConfig.label}
                  </Badge>
                </div>
              </div>
              <button 
                onClick={() => setIsExpanded(false)} 
                className={`${currentTheme.textSecondary} hover:text-white p-1 rounded-full hover:bg-white/10 transition-colors`}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            {/* Real-time Stats Grid with Animated Counters */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              <div className="bg-black/30 rounded-xl p-2 text-center">
                <Users className="h-4 w-4 mx-auto text-blue-400 mb-1" />
                <AnimatedCounter 
                  value={user.total_buyers || 0} 
                  className={`${currentTheme.textPrimary} font-bold text-lg block`}
                />
                <p className={`${currentTheme.textSecondary} text-xs opacity-70`}>Acheteurs</p>
              </div>
              <div className="bg-black/30 rounded-xl p-2 text-center">
                <DollarSign className="h-4 w-4 mx-auto text-green-400 mb-1" />
                <AnimatedCounter 
                  value={user.total_revenue_generated || 0} 
                  prefix="$"
                  className={`${currentTheme.textPrimary} font-bold text-lg block`}
                />
                <p className={`${currentTheme.textSecondary} text-xs opacity-70`}>Générés</p>
              </div>
              <RewardPulse active={animateReward}>
                <div 
                  className={`bg-black/30 rounded-xl p-2 text-center transition-all duration-300 ${
                    animateReward ? 'ring-2 ring-[#f5a623] scale-105' : ''
                  }`}
                >
                  <Percent className="h-4 w-4 mx-auto mb-1" style={{ color: currentTheme.primary }} />
                  <AnimatedCounter 
                    value={user.current_discount_percent} 
                    suffix="%"
                    className="font-bold text-lg block"
                    style={{ color: currentTheme.primary }}
                  />
                  <p className={`${currentTheme.textSecondary} text-xs opacity-70`}>Rabais</p>
                </div>
              </RewardPulse>
            </div>

            {/* Progress to next tier */}
            {nextTierConfig && (
              <div className="mb-4 bg-black/20 rounded-xl p-3">
                <div className="flex justify-between text-xs mb-2">
                  <span className={`${currentTheme.textSecondary} opacity-70`}>Prochain niveau</span>
                  <span style={{ color: currentTheme.primary }} className="flex items-center gap-1">
                    {nextTierConfig.icon} {nextTierConfig.label}
                  </span>
                </div>
                <Progress 
                  value={Math.min((user.total_buyers / 3) * 100, 100)} 
                  className="h-2"
                  style={{
                    '--progress-background': currentTheme.primary
                  }}
                />
                <p className={`${currentTheme.textSecondary} text-xs mt-1 text-center opacity-60`}>
                  {Math.max(3 - user.total_buyers, 0)} acheteur(s) restant(s)
                </p>
              </div>
            )}

            {/* Quick Share Buttons */}
            <div className="flex gap-1 mb-3">
              {SHARE_PLATFORMS.slice(0, 5).map(platform => (
                <button
                  key={platform.id}
                  onClick={() => handleShare(platform.id)}
                  className={`flex-1 ${platform.color} p-2 rounded-lg hover:opacity-90 transition-all hover:scale-105 active:scale-95`}
                  title={platform.label}
                >
                  <span className="text-sm">{platform.icon}</span>
                </button>
              ))}
            </div>

            {/* Copy Link */}
            <div className="flex gap-2">
              <Input
                value={user.referral_link || ""}
                readOnly
                className="bg-black/30 border-white/10 text-xs h-9 flex-1 text-white"
              />
              <Button
                size="sm"
                onClick={copyLink}
                className={`h-9 px-3 ${copied ? "bg-green-600" : ""}`}
                style={{ backgroundColor: copied ? undefined : currentTheme.primary }}
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <Button 
              className="w-full mt-3 bg-white/10 border border-white/20 hover:bg-white/20 text-white"
              size="sm"
              onClick={() => setIsModalOpen(true)}
            >
              Tableau de bord complet <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        )}

        {/* Main Floating Button */}
        <button
          onClick={() => user ? setIsExpanded(!isExpanded) : setShowRegistration(true)}
          className={`group relative flex items-center gap-2 px-4 py-3 rounded-full shadow-lg transition-all duration-300 hover:scale-105 active:scale-95 ${getButtonStyle()} ${tierConfig.glowColor}`}
          style={{
            boxShadow: user 
              ? `0 10px 40px ${currentTheme.primary}50`
              : `0 10px 40px ${currentTheme.primary}40`
          }}
          data-testid="referral-widget-btn"
        >
          {/* Pulse animation for new users */}
          {!user && (
            <span className="absolute -top-1 -right-1 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-white items-center justify-center">
                <Sparkles className="h-2.5 w-2.5" style={{ color: currentTheme.primary }} />
              </span>
            </span>
          )}
          
          {/* Logo in button */}
          <img 
            src={LOGOS.mini} 
            alt="Logo SCENT SCIENCE" 
            className="h-6 w-6 rounded-full object-contain bg-white/20 p-0.5"
          />
          
          {user ? (
            <>
              <div className="flex items-center gap-1">
                <AnimatedCounter 
                  value={user.current_discount_percent} 
                  suffix="%" 
                  className="text-white font-bold"
                />
                <span className="text-white/80 text-sm hidden sm:inline">rabais</span>
              </div>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-white" />
              ) : (
                <ChevronUp className="h-4 w-4 text-white" />
              )}
            </>
          ) : (
            <>
              <Gift className="h-5 w-5 text-black" />
              <span className="text-black font-semibold hidden sm:inline">Gagnez des rabais!</span>
              <span className="text-black font-semibold sm:hidden">Rabais!</span>
            </>
          )}
        </button>
      </div>

      {/* Registration Modal */}
      <Dialog open={showRegistration} onOpenChange={setShowRegistration}>
        <DialogContent 
          className="border-white/10 text-white max-w-sm mx-4"
          style={{ backgroundColor: currentTheme.bgCard.includes('black') ? '#0a0a0a' : '#1a1a2e' }}
        >
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-center justify-center">
              <img src={LOGOS.main} alt="SCENT SCIENCE™" className="h-8" />
            </DialogTitle>
          </DialogHeader>
          
          <div className="text-center mb-4">
            <h3 className="text-xl font-bold mb-2" style={{ color: currentTheme.primary }}>
              Programme de Parrainage
            </h3>
            <p className="text-gray-400 text-sm mb-4">
              Inscrivez-vous et commencez à gagner des rabais en partageant avec vos amis chasseurs!
            </p>
            
            {/* Benefits */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              <div className="bg-white/5 rounded-xl p-3">
                <Trophy className="h-6 w-6 mx-auto mb-1" style={{ color: currentTheme.primary }} />
                <p className="text-white font-bold text-lg">5%</p>
                <p className="text-gray-500 text-xs">Rabais initial</p>
              </div>
              <div className="bg-white/5 rounded-xl p-3">
                <Zap className="h-6 w-6 mx-auto text-purple-500 mb-1" />
                <p className="text-white font-bold text-lg">40%</p>
                <p className="text-gray-500 text-xs">Max possible</p>
              </div>
              <div className="bg-white/5 rounded-xl p-3">
                <Crown className="h-6 w-6 mx-auto mb-1" style={{ color: currentTheme.primary }} />
                <p className="text-white font-bold text-lg">50%</p>
                <p className="text-gray-500 text-xs">Partenaire</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <Label className="text-gray-400">Votre nom</Label>
              <Input
                value={registerForm.name}
                onChange={(e) => setRegisterForm({...registerForm, name: e.target.value})}
                className="bg-white/5 border-white/10 text-white"
                placeholder="Jean Dupont"
              />
            </div>
            <div>
              <Label className="text-gray-400">Votre courriel</Label>
              <Input
                type="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                className="bg-white/5 border-white/10 text-white"
                placeholder="jean@exemple.com"
              />
            </div>
            <Button 
              type="submit" 
              className="w-full h-12 font-semibold text-black"
              style={{ 
                background: `linear-gradient(135deg, ${currentTheme.primary} 0%, ${currentTheme.accent} 50%, ${currentTheme.primary} 100%)` 
              }}
              disabled={registering}
            >
              {registering ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <UserPlus className="h-5 w-5 mr-2" />
                  Rejoindre le programme
                </>
              )}
            </Button>
          </form>

          <p className="text-center text-gray-500 text-xs mt-2">
            Déjà inscrit? Connectez-vous sur la page{" "}
            <a href="/referral" className="hover:underline" style={{ color: currentTheme.primary }}>Parrainage</a>
          </p>
        </DialogContent>
      </Dialog>

      {/* Full Dashboard Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent 
          className="border-white/10 text-white max-w-lg max-h-[80vh] overflow-y-auto mx-4"
          style={{ backgroundColor: '#0a0a0a' }}
        >
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <img src={LOGOS.mini} alt="Logo SCENT SCIENCE" className="h-6 w-6" />
              Mon Programme de Parrainage
            </DialogTitle>
          </DialogHeader>
          
          {user && (
            <div className="space-y-4">
              {/* User Info */}
              <div className={`bg-gradient-to-r ${tierConfig.color} p-4 rounded-xl`}>
                <div className="flex items-center gap-3">
                  <span className="text-4xl">{tierConfig.icon}</span>
                  <div>
                    <p className="text-white font-bold text-lg">{user.name}</p>
                    <p className="text-white/80">Niveau {tierConfig.label}</p>
                    <p className="text-white font-semibold text-2xl">
                      <AnimatedCounter value={user.current_discount_percent} suffix="% de rabais" />
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <Users className="h-8 w-8 mx-auto text-blue-400 mb-2" />
                  <AnimatedCounter 
                    value={user.total_signups || 0} 
                    className="text-3xl font-bold text-white block"
                  />
                  <p className="text-gray-400">Invités</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <TrendingUp className="h-8 w-8 mx-auto text-green-400 mb-2" />
                  <AnimatedCounter 
                    value={user.total_buyers || 0} 
                    className="text-3xl font-bold text-white block"
                  />
                  <p className="text-gray-400">Acheteurs</p>
                </div>
              </div>

              {/* Referral Link */}
              <div className="bg-white/5 rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-2">Votre lien de parrainage:</p>
                <div className="flex gap-2">
                  <Input
                    value={user.referral_link || ""}
                    readOnly
                    className="bg-black/30 border-white/10 font-mono text-sm text-white"
                  />
                  <Button 
                    onClick={copyLink} 
                    className={copied ? "bg-green-600" : ""}
                    style={{ backgroundColor: copied ? undefined : currentTheme.primary }}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
                <p className="text-sm mt-2" style={{ color: currentTheme.primary }}>
                  Code: <span className="font-mono font-bold">{user.referral_code}</span>
                </p>
              </div>

              {/* Share Buttons */}
              <div>
                <p className="text-gray-400 text-sm mb-2">Partager:</p>
                <div className="grid grid-cols-6 gap-2">
                  {SHARE_PLATFORMS.map(platform => (
                    <button
                      key={platform.id}
                      onClick={() => handleShare(platform.id)}
                      className={`${platform.color} p-3 rounded-xl hover:opacity-90 transition-all hover:scale-105 active:scale-95 flex flex-col items-center`}
                      title={platform.label}
                    >
                      <span className="text-lg">{platform.icon}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Progress */}
              {nextTierConfig && (
                <div 
                  className="rounded-xl p-4"
                  style={{ 
                    backgroundColor: `${currentTheme.primary}15`,
                    borderColor: `${currentTheme.primary}30`,
                    borderWidth: '1px'
                  }}
                >
                  <div className="flex justify-between mb-2">
                    <span className="text-white font-medium">Progression</span>
                    <span style={{ color: currentTheme.primary }}>{nextTierConfig.icon} {nextTierConfig.label}</span>
                  </div>
                  <Progress value={Math.min((user.total_buyers / 3) * 100, 100)} className="h-3 mb-2" />
                  <p className="text-gray-400 text-sm text-center">
                    Plus que {Math.max(3 - user.total_buyers, 0)} acheteur(s) pour débloquer le prochain niveau!
                  </p>
                </div>
              )}

              <Button 
                className="w-full bg-white/10 border border-white/20 hover:bg-white/20 text-white"
                onClick={() => {
                  setIsModalOpen(false);
                  window.location.href = "/referral";
                }}
              >
                Voir le tableau de bord complet
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DynamicReferralWidget;
