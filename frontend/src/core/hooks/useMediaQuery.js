/**
 * useMediaQuery - Core Hook
 * ==========================
 * Hook for responsive design with media queries.
 * Architecture LEGO V5 - Core Hook (no business logic)
 * 
 * @module core/hooks
 */
import { useState, useEffect } from 'react';

/**
 * useMediaQuery - Check if a media query matches
 * @param {string} query - CSS media query
 */
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(query);
    
    const handler = (event) => {
      setMatches(event.matches);
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handler);
    } else {
      // Legacy support
      mediaQuery.addListener(handler);
    }

    // Set initial value
    setMatches(mediaQuery.matches);

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handler);
      } else {
        mediaQuery.removeListener(handler);
      }
    };
  }, [query]);

  return matches;
};

/**
 * useBreakpoint - Get current breakpoint
 * Based on Tailwind CSS breakpoints
 */
export const useBreakpoint = () => {
  const isSm = useMediaQuery('(min-width: 640px)');
  const isMd = useMediaQuery('(min-width: 768px)');
  const isLg = useMediaQuery('(min-width: 1024px)');
  const isXl = useMediaQuery('(min-width: 1280px)');
  const is2xl = useMediaQuery('(min-width: 1536px)');

  if (is2xl) return '2xl';
  if (isXl) return 'xl';
  if (isLg) return 'lg';
  if (isMd) return 'md';
  if (isSm) return 'sm';
  return 'xs';
};

/**
 * useIsMobile - Check if current device is mobile
 */
export const useIsMobile = () => {
  return !useMediaQuery('(min-width: 768px)');
};

/**
 * useIsDesktop - Check if current device is desktop
 */
export const useIsDesktop = () => {
  return useMediaQuery('(min-width: 1024px)');
};

/**
 * usePrefersDarkMode - Check if user prefers dark mode
 */
export const usePrefersDarkMode = () => {
  return useMediaQuery('(prefers-color-scheme: dark)');
};

/**
 * usePrefersReducedMotion - Check if user prefers reduced motion
 */
export const usePrefersReducedMotion = () => {
  return useMediaQuery('(prefers-reduced-motion: reduce)');
};

export default useMediaQuery;
