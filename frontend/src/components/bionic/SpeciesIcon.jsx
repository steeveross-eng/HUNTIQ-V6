/**
 * SpeciesIcon - Composant d'affichage d'icône/image d'espèce
 * Design System BIONIC™ compliant
 * Version: 1.0.0
 * 
 * Affiche l'image réelle professionnelle d'une espèce.
 * Remplace TOUS les emojis d'espèces.
 */
import React from 'react';
import { getSpeciesInfo, getSpeciesImage, SPECIES_IMAGES } from '../../config/speciesImages';

/**
 * Tailles prédéfinies pour les icônes
 */
const SIZES = {
  xs: { width: 16, height: 16 },
  sm: { width: 24, height: 24 },
  md: { width: 32, height: 32 },
  lg: { width: 48, height: 48 },
  xl: { width: 64, height: 64 },
  '2xl': { width: 96, height: 96 }
};

/**
 * Composant SpeciesIcon
 * 
 * @param {string} species - ID de l'espèce (deer, moose, bear, etc.)
 * @param {string} size - Taille: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
 * @param {boolean} rounded - Bordure arrondie (défaut: true)
 * @param {boolean} showBorder - Afficher une bordure colorée (défaut: false)
 * @param {string} className - Classes CSS additionnelles
 * @param {object} style - Styles inline additionnels
 * @param {string} alt - Texte alternatif (défaut: nom de l'espèce)
 */
export const SpeciesIcon = ({
  species,
  size = 'md',
  rounded = true,
  showBorder = false,
  className = '',
  style = {},
  alt,
  onClick,
  ...props
}) => {
  const speciesInfo = getSpeciesInfo(species);
  const dimensions = SIZES[size] || SIZES.md;
  const imageUrl = getSpeciesImage(species, size === 'xs' || size === 'sm' ? 'thumbnail' : 'primary');
  
  const containerStyle = {
    width: dimensions.width,
    height: dimensions.height,
    borderRadius: rounded ? '50%' : '4px',
    overflow: 'hidden',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'var(--bionic-bg-hover)',
    border: showBorder ? `2px solid ${speciesInfo?.color || 'var(--bionic-border-secondary)'}` : 'none',
    cursor: onClick ? 'pointer' : 'default',
    flexShrink: 0,
    ...style
  };
  
  const imageStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  };
  
  return (
    <div
      className={`bionic-species-icon ${className}`}
      style={containerStyle}
      onClick={onClick}
      title={speciesInfo?.name || species}
      data-testid={`species-icon-${species}`}
      {...props}
    >
      <img
        src={imageUrl}
        alt={alt || speciesInfo?.name || species}
        style={imageStyle}
        loading="lazy"
        onError={(e) => {
          // Fallback en cas d'erreur de chargement
          e.target.style.display = 'none';
        }}
      />
    </div>
  );
};

/**
 * Composant SpeciesBadge - Badge avec image et texte
 */
export const SpeciesBadge = ({
  species,
  showName = true,
  size = 'sm',
  variant = 'default',
  className = '',
  lang = 'fr'
}) => {
  const speciesInfo = getSpeciesInfo(species);
  
  const variants = {
    default: {
      backgroundColor: 'var(--bionic-bg-hover)',
      color: 'var(--bionic-text-primary)',
      border: '1px solid var(--bionic-border-secondary)'
    },
    colored: {
      backgroundColor: `${speciesInfo?.color}20`,
      color: speciesInfo?.color || 'var(--bionic-text-primary)',
      border: `1px solid ${speciesInfo?.color || 'var(--bionic-border-secondary)'}`
    },
    minimal: {
      backgroundColor: 'transparent',
      color: 'var(--bionic-text-secondary)',
      border: 'none'
    }
  };
  
  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '4px 8px',
    borderRadius: '9999px',
    fontSize: size === 'sm' ? '12px' : '14px',
    fontWeight: 500,
    ...variants[variant]
  };
  
  return (
    <span
      className={`bionic-species-badge ${className}`}
      style={badgeStyle}
      data-testid={`species-badge-${species}`}
    >
      <SpeciesIcon species={species} size="xs" rounded />
      {showName && (
        <span>{lang === 'en' ? speciesInfo?.name_en : speciesInfo?.name}</span>
      )}
    </span>
  );
};

/**
 * Composant SpeciesCard - Carte avec image grande
 */
export const SpeciesCard = ({
  species,
  onClick,
  selected = false,
  disabled = false,
  showStats = false,
  stats = {},
  className = '',
  lang = 'fr'
}) => {
  const speciesInfo = getSpeciesInfo(species);
  
  const cardStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '12px',
    borderRadius: '8px',
    backgroundColor: selected ? `${speciesInfo?.color}15` : 'var(--bionic-bg-card)',
    border: selected 
      ? `2px solid ${speciesInfo?.color}` 
      : '1px solid var(--bionic-border-secondary)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'all 0.2s ease'
  };
  
  return (
    <div
      className={`bionic-species-card ${className}`}
      style={cardStyle}
      onClick={disabled ? undefined : onClick}
      data-testid={`species-card-${species}`}
    >
      <SpeciesIcon species={species} size="xl" rounded showBorder={selected} />
      <span
        style={{
          marginTop: '8px',
          fontSize: '14px',
          fontWeight: 500,
          color: 'var(--bionic-text-primary)',
          textAlign: 'center'
        }}
      >
        {lang === 'en' ? speciesInfo?.name_en : speciesInfo?.name}
      </span>
      {showStats && stats.count !== undefined && (
        <span
          style={{
            marginTop: '4px',
            fontSize: '12px',
            color: 'var(--bionic-text-muted)'
          }}
        >
          {stats.count} observations
        </span>
      )}
    </div>
  );
};

/**
 * Composant SpeciesSelector - Sélecteur de liste d'espèces
 */
export const SpeciesSelectItem = ({
  species,
  selected = false,
  onClick,
  className = '',
  lang = 'fr'
}) => {
  const speciesInfo = getSpeciesInfo(species);
  
  const itemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 12px',
    borderRadius: '6px',
    backgroundColor: selected ? 'var(--bionic-bg-hover)' : 'transparent',
    cursor: 'pointer',
    transition: 'background-color 0.15s ease'
  };
  
  return (
    <div
      className={`bionic-species-select-item ${className}`}
      style={itemStyle}
      onClick={onClick}
      data-testid={`species-select-${species}`}
    >
      <SpeciesIcon species={species} size="sm" rounded />
      <span style={{ 
        flex: 1,
        fontSize: '14px',
        color: 'var(--bionic-text-primary)'
      }}>
        {lang === 'en' ? speciesInfo?.name_en : speciesInfo?.name}
      </span>
      {selected && (
        <span style={{ color: 'var(--bionic-green-primary)' }}>✓</span>
      )}
    </div>
  );
};

export default SpeciesIcon;
