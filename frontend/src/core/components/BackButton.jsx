/**
 * BackButton - Core Component
 * ============================
 * Reusable navigation back button.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Home } from "lucide-react";

/**
 * BackButton - Bouton de retour réutilisable
 * @param {string} label - Texte du bouton (défaut: "Retour")
 * @param {string} to - Destination (défaut: "/" pour accueil, "back" pour history.back())
 * @param {string} variant - Style du bouton: "default", "ghost", "outline"
 * @param {string} className - Classes CSS additionnelles
 * @param {boolean} showIcon - Afficher l'icône (défaut: true)
 * @param {string} iconType - Type d'icône: "arrow" ou "home"
 */
export const BackButton = ({ 
  label = "Retour", 
  to = "/", 
  variant = "ghost",
  className = "",
  showIcon = true,
  iconType = "arrow"
}) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    if (to === "back") {
      window.history.back();
    } else {
      navigate(to);
    }
  };
  
  const Icon = iconType === "home" ? Home : ArrowLeft;
  
  return (
    <Button 
      variant={variant} 
      onClick={handleClick}
      className={`text-gray-400 hover:text-white hover:bg-gray-800/50 ${className}`}
      data-testid="back-button"
    >
      {showIcon && <Icon className="h-4 w-4 mr-2" />}
      {label}
    </Button>
  );
};

/**
 * PageHeaderWithBack - En-tête de page avec bouton retour intégré
 * @param {string} title - Titre de la page
 * @param {string} subtitle - Sous-titre optionnel
 * @param {ReactNode} icon - Icône à afficher
 * @param {string} backTo - Destination du retour
 * @param {string} backLabel - Texte du bouton retour
 */
export const PageHeaderWithBack = ({
  title,
  subtitle,
  icon,
  backTo = "/",
  backLabel = "Retour à l'accueil",
  children
}) => {
  return (
    <div className="mb-6">
      <BackButton label={backLabel} to={backTo} className="mb-4" />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="bg-[#f5a623]/20 p-2.5 rounded-xl">
              {icon}
            </div>
          )}
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">{title}</h1>
            {subtitle && <p className="text-gray-400 text-sm mt-1">{subtitle}</p>}
          </div>
        </div>
        {children}
      </div>
    </div>
  );
};

export default BackButton;
