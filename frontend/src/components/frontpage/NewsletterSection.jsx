import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Mail, Send, Gift, CheckCircle, Sparkles, Bell, Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const NewsletterSection = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    
    setIsSubmitting(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubmitting(false);
    setIsSubscribed(true);
    toast.success('Inscription réussie! Vérifiez votre boîte mail.');
    setEmail('');
    
    // Reset after 5 seconds
    setTimeout(() => setIsSubscribed(false), 5000);
  };

  return (
    <section className="py-16 px-4 bg-gradient-to-r from-[#f5a623]/10 via-[#f5a623]/5 to-transparent border-y border-[#f5a623]/20" data-testid="newsletter-section">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#f5a623]/20 rounded-full mb-6">
            <Mail className="h-8 w-8 text-[#f5a623]" />
          </div>

          {/* Title */}
          <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight mb-4">
            Restez <span className="text-[#f5a623]">connecté</span>
          </h2>
          
          <p className="text-gray-300 text-lg mb-8 max-w-2xl mx-auto">
            Recevez les alertes météo optimales, les nouveaux produits testés et les conseils exclusifs 
            directement dans votre boîte mail.
          </p>

          {/* Benefits */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
            {[
              { icon: Bell, text: 'Alertes météo' },
              { icon: Sparkles, text: 'Nouveautés' },
              { icon: Gift, text: 'Offres exclusives' },
              { icon: Zap, text: 'Conseils pro' },
            ].map((item, i) => (
              <Badge 
                key={i} 
                variant="outline" 
                className="border-[#f5a623]/30 text-gray-300 px-4 py-2"
              >
                <item.icon className="h-4 w-4 mr-2 text-[#f5a623]" />
                {item.text}
              </Badge>
            ))}
          </div>

          {/* Form */}
          {!isSubscribed ? (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <Input
                type="email"
                placeholder="Votre adresse email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 bg-black/50 border-white/10 focus:border-[#f5a623] text-white rounded-sm h-12"
                required
                data-testid="newsletter-email-input"
              />
              <Button 
                type="submit"
                disabled={isSubmitting}
                className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm h-12 px-8 font-bold"
                data-testid="newsletter-submit-btn"
              >
                {isSubmitting ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Inscription...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    S'inscrire
                  </>
                )}
              </Button>
            </form>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center justify-center gap-3 text-green-400"
            >
              <CheckCircle className="h-6 w-6" />
              <span className="text-lg font-semibold">Merci! Vous êtes inscrit.</span>
            </motion.div>
          )}

          {/* Privacy note */}
          <p className="text-gray-500 text-sm mt-4">
            Pas de spam. Désinscription en un clic. Vos données restent au Québec.
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default NewsletterSection;
