/**
 * GlobalContainer - BIONIC™ Global Layout Container
 * ==================================================
 * 
 * Container global pour centrer le contenu avec largeur maximale contrôlée.
 * Architecture LEGO V5 - Module isolé.
 * 
 * Sur les pages secondaires, un padding-left est ajouté pour laisser 
 * l'espace du logo BIONIC (80px + marge).
 */

import React from 'react';
import { useLocation } from 'react-router-dom';

const GlobalContainer = ({ 
  children, 
  className = '',
  maxWidth = '1440px',
  noPadding = false,
  noTopPadding = false,
  noLogoPadding = false,
  fullHeight = false,
  centerContent = false,
  as: Component = 'div'
}) => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  // Pages secondaires: décaler le contenu pour le logo BIONIC (80px + 24px gap)
  const needsLogoPadding = !isHomePage && !noPadding && !noLogoPadding;

  const baseClasses = [
    'w-full',
    'mx-auto',
    fullHeight ? 'min-h-screen' : '',
    centerContent ? 'flex flex-col items-center justify-center' : '',
    noTopPadding ? '' : 'pt-20',
    noPadding ? '' : (needsLogoPadding ? 'pl-28 pr-4 sm:pl-28 sm:pr-6 lg:pl-28 lg:pr-8' : 'px-4 sm:px-6 lg:px-8'),
    className
  ].filter(Boolean).join(' ');

  const style = {
    maxWidth: maxWidth
  };

  return (
    <Component className={baseClasses} style={style}>
      {children}
    </Component>
  );
};

/**
 * PageContainer - Container de page standard BIONIC™
 * Inclut le padding top pour le header fixe
 */
export const PageContainer = ({ 
  children, 
  className = '',
  title,
  subtitle,
  ...props 
}) => (
  <GlobalContainer className={`py-8 ${className}`} {...props}>
    {(title || subtitle) && (
      <div className="mb-8">
        {title && (
          <h1 className="text-3xl md:text-4xl font-bold text-white golden-text">
            {title}
          </h1>
        )}
        {subtitle && (
          <p className="text-gray-400 mt-2">{subtitle}</p>
        )}
      </div>
    )}
    {children}
  </GlobalContainer>
);

/**
 * SectionContainer - Container de section avec espacement vertical
 */
export const SectionContainer = ({ 
  children, 
  className = '',
  noTopPadding = false,
  ...props 
}) => (
  <GlobalContainer 
    noTopPadding={noTopPadding}
    className={`py-12 md:py-16 ${className}`} 
    {...props}
  >
    {children}
  </GlobalContainer>
);

/**
 * AdminContainer - Container pour les pages admin (sans pt pour sidebar)
 */
export const AdminContainer = ({ 
  children, 
  className = '',
  ...props 
}) => (
  <GlobalContainer 
    maxWidth="100%"
    noTopPadding
    noPadding
    className={className} 
    {...props}
  >
    {children}
  </GlobalContainer>
);

/**
 * ContentContainer - Container de contenu centré avec largeur réduite
 * Idéal pour les articles, formulaires, etc.
 */
export const ContentContainer = ({ 
  children, 
  className = '',
  ...props 
}) => (
  <GlobalContainer 
    maxWidth="960px"
    className={`py-8 ${className}`} 
    {...props}
  >
    {children}
  </GlobalContainer>
);

export default GlobalContainer;
