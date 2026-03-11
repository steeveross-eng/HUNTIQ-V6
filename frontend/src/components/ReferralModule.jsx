// ReferralModule.jsx - Module complet de parrainage et partage
import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { 
  Share2,
  Copy,
  Check,
  Users,
  Gift,
  Trophy,
  Star,
  DollarSign,
  TrendingUp,
  Link2,
  Mail,
  MessageCircle,
  Smartphone,
  ExternalLink,
  Crown,
  Award,
  Zap,
  ChevronRight,
  Loader2,
  UserPlus,
  ShoppingCart,
  Percent,
  Facebook,
  Instagram,
  Send,
  Medal
} from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================
// TIER BADGE COMPONENT
// ============================================
const TierBadge = ({ tier, size = "normal" }) => {
  const tierConfig = {
    bronze: { color: "bg-amber-700", Icon: Medal, label: "Bronze" },
    silver: { color: "bg-gray-400", Icon: Medal, label: "Argent" },
    gold: { color: "bg-yellow-500", Icon: Trophy, label: "Or" },
    platinum: { color: "bg-cyan-400", Icon: Award, label: "Platine" },
    diamond: { color: "bg-purple-500", Icon: Crown, label: "Diamant" },
    partner: { color: "bg-gradient-to-r from-[#f5a623] to-purple-600", Icon: Star, label: "Partenaire" }
  };
  
  const config = tierConfig[tier] || tierConfig.bronze;
  const IconComponent = config.Icon;
  
  return (
    <Badge className={`${config.color} text-white ${size === "large" ? "text-lg px-4 py-2" : "px-2 py-1"}`}>
      <IconComponent className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

// ============================================
// SHARE BUTTON COMPONENT
// ============================================
const ShareButton = ({ platform, message, url, onShare }) => {
  const platformConfig = {
    facebook: { icon: Facebook, color: "bg-[#1877F2] hover:bg-[#1565c0]", label: "Facebook" },
    messenger: { icon: MessageCircle, color: "bg-[#0084FF] hover:bg-[#0066cc]", label: "Messenger" },
    instagram: { icon: Instagram, color: "bg-gradient-to-r from-[#833AB4] via-[#E1306C] to-[#F77737] hover:opacity-90", label: "Instagram" },
    tiktok: { icon: Zap, color: "bg-black hover:bg-gray-800", label: "TikTok" },
    whatsapp: { icon: MessageCircle, color: "bg-[#25D366] hover:bg-[#1da851]", label: "WhatsApp" },
    sms: { icon: Smartphone, color: "bg-[#34C759] hover:bg-[#28a745]", label: "SMS" },
    email: { icon: Mail, color: "bg-[#EA4335] hover:bg-[#d33426]", label: "Courriel" },
    copy: { icon: Copy, color: "bg-gray-600 hover:bg-gray-700", label: "Copier" }
  };
  
  const config = platformConfig[platform] || platformConfig.copy;
  const Icon = config.icon;
  
  return (
    <button
      onClick={() => onShare(platform, message, url)}
      className={`flex flex-col items-center justify-center p-4 rounded-xl ${config.color} text-white transition-all hover:scale-105`}
      data-testid={`share-${platform}`}
    >
      <Icon className="h-6 w-6 mb-1" />
      <span className="text-xs font-medium">{config.label}</span>
    </button>
  );
};

// ============================================
// REFERRAL REGISTRATION FORM
// ============================================
const ReferralRegistrationForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: ""
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email) {
      toast.error("Veuillez remplir les champs obligatoires");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/referral/register`, formData);
      toast.success("Compte de parrainage créé!");
      localStorage.setItem("referral_user_id", response.data.user.id);
      localStorage.setItem("referral_code", response.data.referral_code);
      onSuccess(response.data.user);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la création");
    }
    setLoading(false);
  };

  return (
    <Card className="bg-card border-border max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
          <Gift className="h-8 w-8 text-[#f5a623]" />
        </div>
        <CardTitle className="text-white">Rejoignez notre programme de parrainage</CardTitle>
        <CardDescription>
          Partagez, gagnez des rabais et devenez Partenaire Privilégié!
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label className="text-white">Nom complet *</Label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="bg-background border-border"
              placeholder="Jean Dupont"
            />
          </div>
          <div>
            <Label className="text-white">Courriel *</Label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="bg-background border-border"
              placeholder="jean@exemple.com"
            />
          </div>
          <div>
            <Label className="text-white">Téléphone (optionnel)</Label>
            <Input
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="bg-background border-border"
              placeholder="514-555-1234"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full btn-golden text-black h-12"
            disabled={loading}
          >
            {loading ? (
              <><Loader2 className="h-5 w-5 animate-spin mr-2" /> Création...</>
            ) : (
              <><UserPlus className="h-5 w-5 mr-2" /> Créer mon compte</>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

// ============================================
// USER DASHBOARD
// ============================================
const UserDashboard = ({ userId }) => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, [userId]);

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API}/referral/dashboard/${userId}`);
      setDashboard(response.data);
    } catch (error) {
      console.error("Error loading dashboard:", error);
    }
    setLoading(false);
  };

  const copyLink = () => {
    navigator.clipboard.writeText(dashboard?.user?.referral_link || "");
    setCopied(true);
    toast.success("Lien copié!");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = (platform, message, url) => {
    const referralLink = dashboard?.user?.referral_link || "";
    const shareMessages = dashboard?.share_messages || {};
    const platformMessage = shareMessages[platform] || message || "";
    
    const shareUrls = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink)}&quote=${encodeURIComponent(platformMessage)}`,
      messenger: `https://www.facebook.com/dialog/send?link=${encodeURIComponent(referralLink)}&app_id=1&redirect_uri=${encodeURIComponent(referralLink)}`,
      whatsapp: `https://api.whatsapp.com/send?text=${encodeURIComponent(platformMessage + " " + referralLink)}`,
      sms: `sms:?body=${encodeURIComponent(platformMessage + " " + referralLink)}`,
      email: `mailto:?subject=${encodeURIComponent("Découvrez SCENT SCIENCE™!")}&body=${encodeURIComponent(platformMessage + "\n\n" + referralLink)}`
    };

    if (platform === "copy") {
      copyLink();
      return;
    }

    if (platform === "instagram" || platform === "tiktok") {
      // Copy to clipboard for these platforms
      navigator.clipboard.writeText(platformMessage + "\n\n" + referralLink);
      toast.success(`Message copié! Collez-le dans ${platform === "instagram" ? "Instagram" : "TikTok"}`);
      return;
    }

    if (shareUrls[platform]) {
      window.open(shareUrls[platform], "_blank", "width=600,height=400");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p>Erreur lors du chargement du tableau de bord</p>
      </div>
    );
  }

  const { user, invites, rewards, next_tier_info, share_messages } = dashboard;

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Users className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <p className="text-3xl font-bold text-white">{user.total_signups || 0}</p>
            <p className="text-gray-400 text-sm">Invités</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <ShoppingCart className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <p className="text-3xl font-bold text-white">{user.total_buyers || 0}</p>
            <p className="text-gray-400 text-sm">Acheteurs</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <DollarSign className="h-8 w-8 mx-auto mb-2 text-[#f5a623]" />
            <p className="text-3xl font-bold text-white">${(user.total_revenue_generated || 0).toFixed(0)}</p>
            <p className="text-gray-400 text-sm">Revenus générés</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Percent className="h-8 w-8 mx-auto mb-2 text-purple-500" />
            <p className="text-3xl font-bold text-[#f5a623]">{user.current_discount_percent || 5}%</p>
            <p className="text-gray-400 text-sm">Votre rabais</p>
          </CardContent>
        </Card>
      </div>

      {/* Current Level & Progress */}
      <Card className="bg-gradient-to-r from-[#f5a623]/10 to-purple-500/10 border-[#f5a623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <TierBadge tier={user.tier} size="large" />
              <div>
                <p className="text-white font-semibold text-lg">
                  {user.current_discount_percent}% de rabais
                </p>
                <p className="text-gray-400 text-sm">
                  {user.is_partner ? "Partenaire Privilégié" : `Niveau ${user.tier}`}
                </p>
              </div>
            </div>
            {user.is_partner && (
              <Badge className="bg-purple-600 text-white">
                <Crown className="h-4 w-4 mr-1" />
                Commission: {user.partner_commission_rate}%
              </Badge>
            )}
          </div>

          {next_tier_info && !user.is_partner && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">
                  Progression vers <TierBadge tier={next_tier_info.next_tier} />
                </span>
                <span className="text-white">
                  {next_tier_info.buyers_needed} acheteur(s) restant(s)
                </span>
              </div>
              <Progress value={next_tier_info.progress_percent} className="h-3" />
              <p className="text-center text-[#f5a623] text-sm">
                <Gift className="h-4 w-4 inline mr-1" /> Prochain niveau: {next_tier_info.next_discount}% de rabais!
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Referral Link */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Link2 className="h-5 w-5 text-[#f5a623]" />
            Votre lien de parrainage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={user.referral_link}
              readOnly
              className="bg-background border-border font-mono text-sm"
            />
            <Button onClick={copyLink} className={copied ? "bg-green-600" : ""}>
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
          
          <div className="p-3 bg-[#f5a623]/10 rounded-lg">
            <p className="text-[#f5a623] text-sm font-medium">
              Code de parrainage: <span className="font-mono font-bold">{user.referral_code}</span>
            </p>
          </div>

          {/* Share Buttons */}
          <div>
            <p className="text-gray-400 text-sm mb-3">Partagez sur vos réseaux:</p>
            <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
              {["facebook", "messenger", "instagram", "tiktok", "whatsapp", "sms", "email", "copy"].map(platform => (
                <ShareButton
                  key={platform}
                  platform={platform}
                  message={share_messages?.[platform]}
                  url={user.referral_link}
                  onShare={handleShare}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#f5a623]" />
            Activité récente
          </CardTitle>
        </CardHeader>
        <CardContent>
          {invites.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Aucun invité pour le moment</p>
              <p className="text-sm">Partagez votre lien pour commencer!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {invites.slice(0, 5).map((invite, idx) => (
                <div key={invite.id || idx} className="flex items-center justify-between p-3 bg-background rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      invite.status === "purchased" ? "bg-green-500/20" : "bg-blue-500/20"
                    }`}>
                      {invite.status === "purchased" ? (
                        <ShoppingCart className="h-5 w-5 text-green-500" />
                      ) : (
                        <UserPlus className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-white font-medium">
                        {invite.invitee_name || invite.invitee_email}
                      </p>
                      <p className="text-gray-400 text-sm">
                        {invite.status === "purchased" 
                          ? `${invite.total_purchases} achat(s) - $${invite.total_spent?.toFixed(2)}`
                          : "Inscrit"}
                      </p>
                    </div>
                  </div>
                  <Badge variant={invite.status === "purchased" ? "default" : "outline"}>
                    {invite.status === "purchased" ? "Acheteur" : "Invité"}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Rewards History */}
      {rewards.length > 0 && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Gift className="h-5 w-5 text-[#f5a623]" />
              Historique des récompenses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {rewards.slice(0, 5).map((reward, idx) => (
                <div key={reward.id || idx} className="flex items-center justify-between p-3 bg-background rounded-lg">
                  <div className="flex items-center gap-3">
                    <Award className="h-5 w-5 text-[#f5a623]" />
                    <span className="text-white">{reward.description}</span>
                  </div>
                  <span className="text-gray-400 text-sm">
                    {new Date(reward.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Partner CTA */}
      {!user.is_partner && user.total_buyers >= 3 && (
        <Card className="bg-gradient-to-r from-purple-600/20 to-[#f5a623]/20 border-purple-500/30">
          <CardContent className="p-6 text-center">
            <Crown className="h-12 w-12 mx-auto mb-4 text-[#f5a623]" />
            <h3 className="text-xl font-bold text-white mb-2">
              Devenez Partenaire Privilégié!
            </h3>
            <p className="text-gray-300 mb-4">
              Vous êtes éligible pour devenir Partenaire Privilégié et bénéficier de:
            </p>
            <ul className="text-left text-gray-300 space-y-2 mb-6 max-w-sm mx-auto">
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                Rabais exclusifs jusqu&apos;à 50%
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                Commissions sur les ventes de vos invités
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                Accès anticipé aux nouveaux produits
              </li>
              <li className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                Support prioritaire
              </li>
            </ul>
            <Button className="btn-golden text-black">
              <Crown className="h-4 w-4 mr-2" />
              Faire une demande
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// ============================================
// MAIN REFERRAL MODULE
// ============================================
const ReferralModule = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkExistingUser();
  }, []);

  const checkExistingUser = async () => {
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

  if (loading) {
    return (
      <main className="pt-20 min-h-screen bg-background">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
        </div>
      </main>
    );
  }

  return (
    <main className="pt-20 min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-[#f5a623]/10 px-4 py-2 rounded-full mb-4">
            <Share2 className="h-5 w-5 text-[#f5a623]" />
            <span className="text-[#f5a623] font-semibold">Programme de Parrainage</span>
          </div>
          <h1 className="golden-text text-4xl font-bold mb-4">
            Partagez et gagnez!
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Invitez vos amis chasseurs, gagnez des rabais cumulatifs et devenez 
            Partenaire Privilégié pour des avantages exclusifs.
          </p>
        </div>

        {/* Tier Levels Preview */}
        {!user && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-white mb-4 text-center">
              Niveaux de rabais
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { tier: "bronze", buyers: "0-2", discount: "5%" },
                { tier: "silver", buyers: "3-4", discount: "10%" },
                { tier: "gold", buyers: "5-9", discount: "15%" },
                { tier: "platinum", buyers: "10-19", discount: "25%" },
                { tier: "diamond", buyers: "20+", discount: "40%" }
              ].map(level => (
                <Card key={level.tier} className="bg-card border-border text-center p-4">
                  <TierBadge tier={level.tier} />
                  <p className="text-white font-bold text-xl mt-2">{level.discount}</p>
                  <p className="text-gray-400 text-xs">{level.buyers} acheteurs</p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Main Content */}
        {user ? (
          <UserDashboard userId={user.id} />
        ) : (
          <ReferralRegistrationForm onSuccess={setUser} />
        )}
      </div>
    </main>
  );
};

export default ReferralModule;
