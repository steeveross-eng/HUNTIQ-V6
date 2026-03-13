/**
 * BionicLogo - Composant Logo Global V5-ULTIME-FUSION
 * 
 * DIRECTIVES:
 * - PAGE PRINCIPALE: logo grand (211px), sous header, position libre
 * - PAGES SECONDAIRES: logo 80px, sous navbar, contenu décalé à droite
 * - TOUTES PAGES: transparent (mix-blend-mode: screen)
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

// Taille du logo sur pages secondaires — exportée pour alignement global
export const INNER_LOGO_SIZE = 80;
export const INNER_LOGO_LEFT = 12;

export const BionicLogoGlobal = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  
  const logoSize = isHomePage ? 211 : INNER_LOGO_SIZE;
  const topPos = isHomePage ? '80px' : '72px';
  
  return (
    <Link 
      to="/"
      style={{
        position: 'fixed',
        top: topPos,
        left: `${INNER_LOGO_LEFT}px`,
        zIndex: 50,
        width: `${logoSize}px`,
        height: `${logoSize}px`,
        display: 'block',
        perspective: '1000px',
      }}
      data-testid="bionic-logo-global"
      aria-label="BIONIC - Retour à l'accueil"
    >
      <OptimizedImage 
        src="/logos/bionic-logo-official.png"
        alt="BIONIC Chasse / Hunt"
        width={logoSize}
        height={logoSize}
        className="bionic-logo-3d-rotate"
        loading={isHomePage ? 'eager' : 'lazy'}
        fetchpriority={isHomePage ? 'high' : undefined}
        style={{
          width: `${logoSize}px`,
          height: `${logoSize}px`,
          objectFit: 'contain',
          mixBlendMode: 'screen'
        }}
      />
    </Link>
  );
};

const BionicLogo = ({ className = '' }) => {
  return (
    <OptimizedImage 
      src="/logos/bionic-logo-official.png"
      alt="BIONIC"
      width={32}
      height={32}
      className={`bionic-logo-3d-rotate ${className}`}
      style={{ 
        width: '32px', 
        height: '32px',
        objectFit: 'contain',
        mixBlendMode: 'screen'
      }}
    />
  );
};

export default BionicLogo;
