/**
 * OptimizedImage - Composant Image Optimisé BRANCHE 1 POLISH FINAL
 * 
 * Utilise automatiquement le format le plus performant (AVIF > WebP > PNG/JPG)
 * avec fallback pour les navigateurs non compatibles.
 * Conforme WCAG AAA et Core Web Vitals.
 * 
 * @module OptimizedImage
 * @version 1.0.0
 * @phase POLISH_FINAL
 */

import React, { memo } from 'react';

/**
 * Génère les chemins pour les formats optimisés
 * @param {string} src - Chemin source de l'image
 * @returns {object} - Chemins AVIF, WebP et original
 */
const getOptimizedPaths = (src) => {
  if (!src) return { avif: null, webp: null, original: src };
  
  // Extraire le chemin de base et l'extension
  const lastDot = src.lastIndexOf('.');
  if (lastDot === -1) return { avif: null, webp: null, original: src };
  
  const basePath = src.substring(0, lastDot);
  const extension = src.substring(lastDot + 1).toLowerCase();
  
  // Ne pas convertir SVG ou formats déjà optimisés
  if (['svg', 'webp', 'avif'].includes(extension)) {
    return { avif: null, webp: null, original: src };
  }
  
  // Générer les chemins optimisés pour PNG, JPG, JPEG
  if (['png', 'jpg', 'jpeg'].includes(extension)) {
    return {
      avif: `${basePath}.avif`,
      webp: `${basePath}.webp`,
      original: src
    };
  }
  
  return { avif: null, webp: null, original: src };
};

/**
 * OptimizedImage Component
 * 
 * @param {string} src - Chemin source de l'image (PNG/JPG)
 * @param {string} alt - Texte alternatif (WCAG obligatoire)
 * @param {string} className - Classes CSS
 * @param {object} style - Styles inline
 * @param {number} width - Largeur (pour CLS)
 * @param {number} height - Hauteur (pour CLS)
 * @param {string} loading - 'lazy' | 'eager' (défaut: 'lazy')
 * @param {string} fetchpriority - 'high' | 'low' | 'auto'
 * @param {string} decoding - 'async' | 'sync' | 'auto'
 * @param {function} onLoad - Callback au chargement
 * @param {function} onError - Callback en cas d'erreur
 */
const OptimizedImage = memo(({
  src,
  alt,
  className = '',
  style = {},
  width,
  height,
  loading = 'lazy',
  fetchpriority,
  decoding = 'async',
  onLoad,
  onError,
  'data-testid': testId,
  ...rest
}) => {
  const { avif, webp, original } = getOptimizedPaths(src);
  
  // Attributs communs pour l'image
  const imgProps = {
    alt: alt || '',
    className,
    style,
    width,
    height,
    loading,
    decoding,
    onLoad,
    onError,
    'data-testid': testId,
    ...rest
  };
  
  // Ajouter fetchpriority seulement si spécifié (évite les warnings)
  if (fetchpriority) {
    imgProps.fetchPriority = fetchpriority;
  }
  
  // Si pas de formats optimisés disponibles, utiliser une img simple
  if (!avif && !webp) {
    return <img src={original} {...imgProps} />;
  }
  
  // Utiliser <picture> pour le support multi-format avec fallback
  return (
    <picture>
      {/* AVIF - Meilleure compression, support moderne */}
      {avif && (
        <source srcSet={avif} type="image/avif" />
      )}
      
      {/* WebP - Bonne compression, support large */}
      {webp && (
        <source srcSet={webp} type="image/webp" />
      )}
      
      {/* Fallback PNG/JPG pour les navigateurs anciens */}
      <img src={original} {...imgProps} />
    </picture>
  );
});

OptimizedImage.displayName = 'OptimizedImage';

export default OptimizedImage;
export { OptimizedImage, getOptimizedPaths };
