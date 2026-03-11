// ReferralWidget.jsx - Widget flottant de parrainage avec compteur en temps réel
import { useState, useEffect } from "react";
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
  Facebook,
  MessageCircle,
  Instagram,
  Smartphone,
  Mail,
  Zap,
  Trophy,
  ArrowRight,
  UserPlus,
  Medal,
  Award,
  Star,
  Loader2
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tier configuration - using lucide icons
const TIER_CONFIG = {
  bronze: { color: "from-amber-700 to-amber-900", Icon: Medal, label: "Bronze", next: "silver" },
  silver: { color: "from-gray-400 to-gray-600", Icon: Medal, label: "Argent", next: "gold" },
  gold: { color: "from-yellow-500 to-yellow-700", Icon: Trophy, label: "Or", next: "platinum" },
  platinum: { color: "from-cyan-400 to-cyan-600", Icon: Award, label: "Platine", next: "diamond" },
  diamond: { color: "from-purple-500 to-purple-700", Icon: Crown, label: "Diamant", next: null },
  partner: { color: "from-[#f5a623] to-purple-600", Icon: Star, label: "Partenaire", next: null }
};

// Share platforms
const SHARE_PLATFORMS = [
  { id: "facebook", icon: Facebook, color: "bg-[#1877F2]", label: "Facebook" },
  { id: "whatsapp", icon: MessageCircle, color: "bg-[#25D366]", label: "WhatsApp" },
  { id: "instagram", icon: Instagram, color: "bg-gradient-to-r from-[#833AB4] via-[#E1306C] to-[#F77737]", label: "Instagram" },
  { id: "sms", icon: Smartphone, color: "bg-[#34C759]", label: "SMS" },
  { id: "email", icon: Mail, color: "bg-[#EA4335]", label: "Email" },
  { id: "copy", icon: Copy, color: "bg-gray-600", label: "Copier" }
];

const ReferralWidget = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const [registerForm, setRegisterForm] = useState({ name: "", email: "" });
  const [registering, setRegistering] = useState(false);
  
  // Animation state for rewards counter
  const [animateReward, setAnimateReward] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    const savedUserId = localStorage.getItem("referral_user_id");
    const savedEmail = localStorage.getItem("user_email");
    
    if (savedUserId) {
      try {
        const response = await axios.get(`${API}/referral/dashboard/${savedUserId}`);
        setUser(response.data.user);
      } catch (error) {
        localStorage.removeItem("referral_user_id");
      }
    } else if (savedEmail) {
      try {
        const response = await axios.get(`${API}/referral/user/${encodeURIComponent(savedEmail)}`);
        setUser(response.data);
        localStorage.setItem("referral_user_id", response.data.id);
      } catch (error) {
        // User doesn't have a referral account yet
      }
    }
    setLoading(false);
  };

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
      setShowRegistration(false);
      setAnimateReward(true);
      setTimeout(() => setAnimateReward(false), 2000);
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
  if (window.location.pathname.startsWith("/admin")) {
    return null;
  }

  return (
    <>
      {/* Floating Widget Button */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2">
        {/* Expanded Quick Stats */}
        {isExpanded && user && (
          <div className="bg-card border border-border rounded-2xl p-4 shadow-2xl animate-in slide-in-from-bottom-2 duration-300 w-72">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <tierConfig.Icon className="h-6 w-6 text-white" />
                <div>
                  <p className="text-white font-semibold">{user.name}</p>
                  <Badge className={`bg-gradient-to-r ${tierConfig.color} text-white text-xs`}>
                    {tierConfig.label}
                  </Badge>
                </div>
              </div>
              <button onClick={() => setIsExpanded(false)} className="text-gray-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="bg-background rounded-lg p-2 text-center">
                <Users className="h-4 w-4 mx-auto text-blue-500 mb-1" />
                <p className="text-white font-bold">{user.total_buyers || 0}</p>
                <p className="text-gray-500 text-xs">Acheteurs</p>
              </div>
              <div className="bg-background rounded-lg p-2 text-center">
                <DollarSign className="h-4 w-4 mx-auto text-green-500 mb-1" />
                <p className="text-white font-bold">${(user.total_revenue_generated || 0).toFixed(0)}</p>
                <p className="text-gray-500 text-xs">Générés</p>
              </div>
              <div className={`bg-background rounded-lg p-2 text-center ${animateReward ? "animate-pulse ring-2 ring-[#f5a623]" : ""}`}>
                <Percent className="h-4 w-4 mx-auto text-[#f5a623] mb-1" />
                <p className="text-[#f5a623] font-bold">{user.current_discount_percent}%</p>
                <p className="text-gray-500 text-xs">Rabais</p>
              </div>
            </div>

            {/* Progress to next tier */}
            {nextTierConfig && (
              <div className="mb-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Prochain niveau</span>
                  <span className="text-[#f5a623] flex items-center gap-1">
                    <nextTierConfig.Icon className="h-3 w-3" /> {nextTierConfig.label}
                  </span>
                </div>
                <Progress value={Math.min((user.total_buyers / 3) * 100, 100)} className="h-2" />
              </div>
            )}

            {/* Quick Share Buttons */}
            <div className="flex gap-1 mb-3">
              {SHARE_PLATFORMS.slice(0, 5).map(platform => (
                <button
                  key={platform.id}
                  onClick={() => handleShare(platform.id)}
                  className={`flex-1 ${platform.color} p-2 rounded-lg hover:opacity-90 transition-opacity`}
                  title={platform.label}
                >
                  <platform.icon className="h-4 w-4 mx-auto text-white" />
                </button>
              ))}
            </div>

            {/* Copy Link */}
            <div className="flex gap-2">
              <Input
                value={user.referral_link || ""}
                readOnly
                className="bg-background border-border text-xs h-8 flex-1"
              />
              <Button
                size="sm"
                onClick={copyLink}
                className={copied ? "bg-green-600" : "bg-[#f5a623] hover:bg-[#d4850e]"}
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <Button 
              className="w-full mt-3 bg-transparent border border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10"
              size="sm"
              onClick={() => setIsModalOpen(true)}
            >
              Voir mon tableau de bord <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        )}

        {/* Main Floating Button */}
        <button
          onClick={() => user ? setIsExpanded(!isExpanded) : setShowRegistration(true)}
          className={`group relative flex items-center gap-2 px-4 py-3 rounded-full shadow-lg transition-all duration-300 hover:scale-105 ${
            user 
              ? `bg-gradient-to-r ${tierConfig.color}` 
              : "bg-gradient-to-r from-[#f5a623] to-[#d4850e]"
          }`}
          data-testid="referral-widget-btn"
        >
          {/* Pulse animation for new users */}
          {!user && (
            <span className="absolute -top-1 -right-1 flex h-4 w-4">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-white items-center justify-center">
                <Sparkles className="h-2.5 w-2.5 text-[#f5a623]" />
              </span>
            </span>
          )}
          
          {user ? (
            <>
              <Gift className="h-5 w-5 text-white" />
              <span className="text-white font-semibold">
                {user.current_discount_percent}% rabais
              </span>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-white" />
              ) : (
                <ChevronUp className="h-4 w-4 text-white" />
              )}
            </>
          ) : (
            <>
              <Gift className="h-5 w-5 text-black" />
              <span className="text-black font-semibold">Gagnez des rabais!</span>
            </>
          )}
        </button>
      </div>

      {/* Registration Modal */}
      <Dialog open={showRegistration} onOpenChange={setShowRegistration}>
        <DialogContent className="bg-card border-border text-white max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-center justify-center">
              <Gift className="h-6 w-6 text-[#f5a623]" />
              Programme de Parrainage
            </DialogTitle>
          </DialogHeader>
          
          <div className="text-center mb-4">
            <p className="text-gray-400 mb-4">
              Inscrivez-vous et commencez à gagner des rabais en partageant avec vos amis chasseurs!
            </p>
            
            {/* Benefits */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              <div className="bg-background rounded-lg p-3">
                <Trophy className="h-6 w-6 mx-auto text-yellow-500 mb-1" />
                <p className="text-white font-bold text-lg">5%</p>
                <p className="text-gray-500 text-xs">Rabais initial</p>
              </div>
              <div className="bg-background rounded-lg p-3">
                <Zap className="h-6 w-6 mx-auto text-purple-500 mb-1" />
                <p className="text-white font-bold text-lg">40%</p>
                <p className="text-gray-500 text-xs">Max possible</p>
              </div>
              <div className="bg-background rounded-lg p-3">
                <Crown className="h-6 w-6 mx-auto text-[#f5a623] mb-1" />
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
                className="bg-background border-border"
                placeholder="Jean Dupont"
              />
            </div>
            <div>
              <Label className="text-gray-400">Votre courriel</Label>
              <Input
                type="email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                className="bg-background border-border"
                placeholder="jean@exemple.com"
              />
            </div>
            <Button 
              type="submit" 
              className="w-full btn-golden text-black h-12 font-semibold"
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
            <a href="/referral" className="text-[#f5a623] hover:underline">Parrainage</a>
          </p>
        </DialogContent>
      </Dialog>

      {/* Full Dashboard Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="bg-card border-border text-white max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Gift className="h-5 w-5 text-[#f5a623]" />
              Mon Programme de Parrainage
            </DialogTitle>
          </DialogHeader>
          
          {user && (
            <div className="space-y-4">
              {/* User Info */}
              <div className={`bg-gradient-to-r ${tierConfig.color} p-4 rounded-xl`}>
                <div className="flex items-center gap-3">
                  <tierConfig.Icon className="h-10 w-10 text-white" />
                  <div>
                    <p className="text-white font-bold text-lg">{user.name}</p>
                    <p className="text-white/80">Niveau {tierConfig.label}</p>
                    <p className="text-white font-semibold text-2xl">{user.current_discount_percent}% de rabais</p>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-background rounded-xl p-4 text-center">
                  <Users className="h-8 w-8 mx-auto text-blue-500 mb-2" />
                  <p className="text-3xl font-bold text-white">{user.total_signups || 0}</p>
                  <p className="text-gray-400">Invités</p>
                </div>
                <div className="bg-background rounded-xl p-4 text-center">
                  <DollarSign className="h-8 w-8 mx-auto text-green-500 mb-2" />
                  <p className="text-3xl font-bold text-white">{user.total_buyers || 0}</p>
                  <p className="text-gray-400">Acheteurs</p>
                </div>
              </div>

              {/* Referral Link */}
              <div className="bg-background rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-2">Votre lien de parrainage:</p>
                <div className="flex gap-2">
                  <Input
                    value={user.referral_link || ""}
                    readOnly
                    className="bg-card border-border font-mono text-sm"
                  />
                  <Button onClick={copyLink} className={copied ? "bg-green-600" : ""}>
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
                <p className="text-[#f5a623] text-sm mt-2">
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
                      className={`${platform.color} p-3 rounded-xl hover:opacity-90 transition-opacity flex flex-col items-center`}
                      title={platform.label}
                    >
                      <platform.icon className="h-5 w-5 text-white" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Progress */}
              {nextTierConfig && (
                <div className="bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-xl p-4">
                  <div className="flex justify-between mb-2">
                    <span className="text-white font-medium">Progression</span>
                    <span className="text-[#f5a623] flex items-center gap-1">
                      <nextTierConfig.Icon className="h-4 w-4" /> {nextTierConfig.label}
                    </span>
                  </div>
                  <Progress value={Math.min((user.total_buyers / 3) * 100, 100)} className="h-3 mb-2" />
                  <p className="text-gray-400 text-sm text-center">
                    Plus que {Math.max(3 - user.total_buyers, 0)} acheteur(s) pour débloquer le prochain niveau!
                  </p>
                </div>
              )}

              <Button 
                className="w-full bg-transparent border border-gray-600 text-gray-300 hover:bg-gray-800"
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

export default ReferralWidget;
