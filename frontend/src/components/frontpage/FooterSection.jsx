import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  MapPin, Phone, Mail, Clock, Facebook, Instagram, Youtube,
  Twitter, Linkedin, ChevronRight, ExternalLink, Heart
} from 'lucide-react';
import BionicLogo from '@/components/BionicLogo';

const FooterSection = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    produits: [
      { label: 'Attractants', href: '/shop?category=attractants' },
      { label: 'Caméras Trail', href: '/shop?category=cameras' },
      { label: 'Appeaux', href: '/shop?category=appeaux' },
      { label: 'Accessoires', href: '/shop?category=accessories' },
      { label: 'Nouveautés', href: '/shop?new=true' },
    ],
    services: [
      { label: 'Analyse BIONIC™', href: '/analyze' },
      { label: 'Carte des Territoires', href: '/territoire' },
      { label: 'Formations', href: '/formations' },
      { label: 'Marketplace', href: '/marketplace' },
      { label: 'Communauté', href: '/networking' },
    ],
    ressources: [
      { label: 'Blog', href: '/blog' },
      { label: 'Guide du Chasseur', href: '/guide' },
      { label: 'FAQ', href: '/faq' },
      { label: 'Règlements Québec', href: 'https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse', external: true },
      { label: 'FédéCP', href: 'https://fedecp.com', external: true },
    ],
    entreprise: [
      { label: 'À propos', href: '/about' },
      { label: 'Partenaires', href: '/partners' },
      { label: 'Devenir Partenaire', href: '/become-partner' },
      { label: 'Carrières', href: '/careers' },
      { label: 'Contact', href: '/contact' },
    ]
  };

  const socialLinks = [
    { icon: Facebook, href: 'https://facebook.com/huntiqbionic', label: 'Facebook' },
    { icon: Instagram, href: 'https://instagram.com/huntiqbionic', label: 'Instagram' },
    { icon: Youtube, href: 'https://youtube.com/@huntiqbionic', label: 'YouTube' },
    { icon: Twitter, href: 'https://twitter.com/huntiqbionic', label: 'Twitter' },
  ];

  return (
    <footer className="bg-[#0a0a0a] border-t border-white/5" data-testid="footer-section">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <BionicLogo className="h-10 w-10" />
              <span className="font-barlow text-2xl font-bold text-white">BIONIC™</span>
            </Link>
            <p className="text-gray-300 text-sm mb-6 max-w-xs">
              La plateforme de chasse intelligente du Québec. Analyse de territoire, 
              attractants testés scientifiquement, et communauté de chasseurs passionnés.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-gray-300 text-sm">
                <MapPin className="h-4 w-4 text-[#f5a623]" />
                <span>Québec, Canada</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300 text-sm">
                <Mail className="h-4 w-4 text-[#f5a623]" />
                <a href="mailto:info@huntiq.ca" className="hover:text-white transition-colors">
                  info@huntiq.ca
                </a>
              </div>
              <div className="flex items-center gap-2 text-gray-300 text-sm">
                <Clock className="h-4 w-4 text-[#f5a623]" />
                <span>Lun-Ven: 9h-17h EST</span>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-3 mt-6">
              {socialLinks.map((social, i) => (
                <a
                  key={i}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center hover:bg-[#f5a623]/20 hover:text-[#f5a623] transition-colors text-gray-300"
                  aria-label={social.label}
                >
                  <social.icon className="h-5 w-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Links Columns */}
          <div>
            <h3 className="text-white font-bold uppercase tracking-wider text-sm mb-4">Produits</h3>
            <ul className="space-y-2">
              {footerLinks.produits.map((link, i) => (
                <li key={i}>
                  <Link 
                    to={link.href}
                    className="text-gray-300 text-sm hover:text-[#f5a623] transition-colors flex items-center gap-1"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold uppercase tracking-wider text-sm mb-4">Services</h3>
            <ul className="space-y-2">
              {footerLinks.services.map((link, i) => (
                <li key={i}>
                  <Link 
                    to={link.href}
                    className="text-gray-300 text-sm hover:text-[#f5a623] transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold uppercase tracking-wider text-sm mb-4">Ressources</h3>
            <ul className="space-y-2">
              {footerLinks.ressources.map((link, i) => (
                <li key={i}>
                  {link.external ? (
                    <a 
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-300 text-sm hover:text-[#f5a623] transition-colors flex items-center gap-1"
                    >
                      {link.label}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <Link 
                      to={link.href}
                      className="text-gray-300 text-sm hover:text-[#f5a623] transition-colors"
                    >
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-bold uppercase tracking-wider text-sm mb-4">Entreprise</h3>
            <ul className="space-y-2">
              {footerLinks.entreprise.map((link, i) => (
                <li key={i}>
                  <Link 
                    to={link.href}
                    className="text-gray-300 text-sm hover:text-[#f5a623] transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-wrap items-center justify-center gap-4 text-gray-500 text-sm">
              <span>© {currentYear} BIONIC HUNT/Chasse BIONIC™. Tous droits réservés.</span>
              <span className="hidden md:inline">•</span>
              <Link to="/privacy" className="hover:text-white transition-colors">
                Politique de confidentialité
              </Link>
              <span className="hidden md:inline">•</span>
              <Link to="/terms" className="hover:text-white transition-colors">
                Conditions d'utilisation
              </Link>
              <span className="hidden md:inline">•</span>
              <Link to="/cookies" className="hover:text-white transition-colors">
                Cookies
              </Link>
            </div>
            
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <span>Fait avec</span>
              <Heart className="h-4 w-4 text-red-500 fill-red-500" />
              <span>au Québec</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default FooterSection;
