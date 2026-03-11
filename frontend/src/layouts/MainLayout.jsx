/**
 * MainLayout - Main application layout with header and navigation
 * Extracted from App.js for better maintainability
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { UserMenu, useAuth } from '@/components/GlobalAuth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ShoppingCart,
  Menu,
  Globe,
  Settings,
  LogIn,
  Map,
  Users,
  GraduationCap,
  FileText
} from 'lucide-react';

const MainLayout = ({ children, cart = [], onLanguageChange }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, openLoginModal } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [language, setLanguage] = React.useState('FR');

  const navLinks = [
    { path: "/", label: "Accueil" },
    { path: "/analyze", label: "Analysez" },
    { path: "/compare", label: "Comparez" },
    { path: "/shop", label: "Magasin" },
    { path: "/territory", label: "Territoire", Icon: Map },
    { path: "/permis-chasse", label: "Permis de chasse", Icon: FileText },
    { path: "/marketplace", label: "Marketplace", Icon: ShoppingCart },
    { path: "/network", label: "Réseau", Icon: Users },
    { path: "/formations", label: "Formations", Icon: GraduationCap },
  ];

  const cartItemCount = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    if (onLanguageChange) onLanguageChange(newLang);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-lg border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <img 
                src="/logo192.png" 
                alt="Logo" 
                className="h-10 w-10 object-contain"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-sm font-medium transition-colors hover:text-[#f5a623] flex items-center gap-1 ${
                    location.pathname === link.path ? 'text-[#f5a623]' : 'text-gray-300'
                  }`}
                >
                  {link.Icon && <link.Icon className="h-4 w-4" />}
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Right Actions */}
            <div className="flex items-center space-x-4">
              {/* Auth Button */}
              {isAuthenticated ? (
                <UserMenu />
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={openLoginModal}
                  className="border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623] hover:text-black"
                  data-testid="header-login-btn"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Connexion
                </Button>
              )}

              {/* Language Selector */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-gray-300">
                    <Globe className="h-4 w-4 mr-1" />
                    {language}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => handleLanguageChange('FR')}>
                    FR - Français
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleLanguageChange('EN')}>
                    EN - English
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Settings */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin')}
                className="text-gray-300 hover:text-[#f5a623]"
              >
                <Settings className="h-5 w-5" />
              </Button>

              {/* Cart */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/shop')}
                className="text-gray-300 hover:text-[#f5a623] relative"
              >
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-[#f5a623] text-black text-xs">
                    {cartItemCount}
                  </Badge>
                )}
                <span className="ml-2 hidden sm:inline">Panier</span>
              </Button>

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="sm"
                className="md:hidden text-gray-300"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                <Menu className="h-6 w-6" />
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-black/95 border-t border-border">
            <div className="px-4 py-4 space-y-2">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-2 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.path 
                      ? 'bg-[#f5a623]/20 text-[#f5a623]' 
                      : 'text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  {link.Icon && <link.Icon className="h-4 w-4" />}
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="pt-16">
        {children}
      </main>

      {/* Footer could be added here */}
    </div>
  );
};

export default MainLayout;
