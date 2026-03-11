import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Users, MessageCircle, Heart, Share2, Camera, MapPin,
  Trophy, Star, Crown, Medal, ChevronRight, UserPlus
} from 'lucide-react';
import { motion } from 'framer-motion';

const CommunitySection = () => {
  const posts = [
    {
      id: 1,
      user: { name: 'Marc T.', avatar: 'https://i.pravatar.cc/100?img=1', badge: 'Expert' },
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      caption: 'Premier orignal de la saison! Zone 17, 850 lbs 🦌',
      likes: 234,
      comments: 45,
      location: 'Laurentides, QC'
    },
    {
      id: 2,
      user: { name: 'Sophie L.', avatar: 'https://i.pravatar.cc/100?img=5', badge: 'Pro' },
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      caption: 'Magnifique buck 12 pointes. La patience paie!',
      likes: 456,
      comments: 78,
      location: 'Mauricie, QC'
    },
    {
      id: 3,
      user: { name: 'Jean-Pierre B.', avatar: 'https://i.pravatar.cc/100?img=3', badge: null },
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      caption: 'Setup caméra trail parfait. 3 semaines de repérage.',
      likes: 189,
      comments: 32,
      location: 'Abitibi, QC'
    },
    {
      id: 4,
      user: { name: 'Marie G.', avatar: 'https://i.pravatar.cc/100?img=9', badge: 'Guide' },
      image: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      caption: 'Lever de soleil sur mon territoire préféré ☀️',
      likes: 567,
      comments: 89,
      location: 'Saguenay, QC'
    },
  ];

  const leaderboard = [
    { rank: 1, name: 'PatrickChasseur', points: 15420, badge: 'crown' },
    { rank: 2, name: 'MarcOrignal', points: 12340, badge: 'medal' },
    { rank: 3, name: 'SophieHunt', points: 11890, badge: 'medal' },
    { rank: 4, name: 'JeanPierrePro', points: 9870, badge: null },
    { rank: 5, name: 'MarieLaurentides', points: 8540, badge: null },
  ];

  const getBadgeIcon = (badge) => {
    switch(badge) {
      case 'crown': return <Crown className="h-4 w-4 text-[#f5a623]" />;
      case 'medal': return <Medal className="h-4 w-4 text-gray-300" />;
      default: return null;
    }
  };

  const getUserBadgeColor = (badge) => {
    switch(badge) {
      case 'Expert': return 'bg-purple-500/20 text-purple-400';
      case 'Pro': return 'bg-blue-500/20 text-blue-400';
      case 'Guide': return 'bg-green-500/20 text-green-400';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  return (
    <section className="py-16 px-4 bg-[#0a0a0a]" data-testid="community-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Users className="h-6 w-6 text-[#f5a623]" />
            <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Communauté</span>
          </div>
          <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
            Chasseurs <span className="text-[#f5a623]">BIONIC™</span>
          </h2>
          <p className="text-gray-300 mt-2">Rejoignez plus de 12,000 chasseurs passionnés</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Photo Grid */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {posts.map((post, i) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden group cursor-pointer hover:border-[#f5a623]/30 transition-colors">
                    <div className="relative aspect-square overflow-hidden">
                      <img 
                        src={post.image}
                        alt={post.caption}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                      {/* Overlay */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-3">
                        {/* User info */}
                        <div className="flex items-center gap-2">
                          <img 
                            src={post.user.avatar}
                            alt={post.user.name}
                            className="w-8 h-8 rounded-full border-2 border-[#f5a623]"
                          />
                          <div>
                            <p className="text-white text-sm font-medium">{post.user.name}</p>
                            {post.user.badge && (
                              <Badge className={`text-xs ${getUserBadgeColor(post.user.badge)}`}>
                                {post.user.badge}
                              </Badge>
                            )}
                          </div>
                        </div>
                        
                        {/* Caption */}
                        <p className="text-white text-sm line-clamp-2">{post.caption}</p>
                        
                        {/* Stats */}
                        <div className="flex items-center gap-4 text-white text-sm">
                          <span className="flex items-center gap-1">
                            <Heart className="h-4 w-4 text-red-400" /> {post.likes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle className="h-4 w-4" /> {post.comments}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Join CTA */}
            <div className="mt-6 text-center">
              <Button className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm px-8">
                <Camera className="h-4 w-4 mr-2" />
                Partager votre prise
              </Button>
            </div>
          </div>

          {/* Leaderboard */}
          <div>
            <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden sticky top-24">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Trophy className="h-5 w-5 text-[#f5a623]" />
                  <h3 className="text-white font-bold">Classement</h3>
                </div>

                <div className="space-y-3">
                  {leaderboard.map((user, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      viewport={{ once: true }}
                      className={`flex items-center gap-3 p-2 rounded-sm ${
                        user.rank === 1 ? 'bg-[#f5a623]/10 border border-[#f5a623]/30' : 'bg-black/30'
                      }`}
                    >
                      <div className={`w-6 h-6 flex items-center justify-center rounded-full text-sm font-bold ${
                        user.rank === 1 ? 'bg-[#f5a623] text-black' :
                        user.rank <= 3 ? 'bg-gray-600 text-white' :
                        'bg-gray-800 text-gray-300'
                      }`}>
                        {user.rank}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-white text-sm font-medium truncate">{user.name}</span>
                          {getBadgeIcon(user.badge)}
                        </div>
                        <span className="text-gray-500 text-xs">{user.points.toLocaleString()} pts</span>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <Button 
                  variant="outline" 
                  className="w-full mt-4 border-white/20 text-gray-300 hover:border-[#f5a623] hover:text-[#f5a623] rounded-sm"
                >
                  Voir le classement complet
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>

                {/* Join Community */}
                <div className="mt-6 pt-4 border-t border-white/10">
                  <p className="text-gray-300 text-sm mb-3">Pas encore membre?</p>
                  <Button className="w-full bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm">
                    <UserPlus className="h-4 w-4 mr-2" />
                    Rejoindre
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CommunitySection;
