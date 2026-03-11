/**
 * ScrollNavigator - Navigation arrows for scrolling up/down pages
 * Fixed position arrows centered horizontally at top and bottom of screen
 * 
 * Features:
 * - Arrow up (↑) fixed at top center - appears after scrolling
 * - Arrow down (↓) fixed at bottom center - with pulsing animation
 * - Smooth scroll animation
 * - High visibility design with golden accent
 * - Responsive and cross-browser compatible
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

const ScrollNavigator = () => {
  const [showTopArrow, setShowTopArrow] = useState(false);
  const [showBottomArrow, setShowBottomArrow] = useState(true); // Always show initially

  // Handle scroll events to show/hide arrows
  const handleScroll = useCallback(() => {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    // Show top arrow after scrolling down 150px
    setShowTopArrow(scrollY > 150);
    
    // Show bottom arrow always EXCEPT when at the very bottom of a scrollable page
    const hasScrollableContent = documentHeight > windowHeight + 50;
    const atBottom = scrollY + windowHeight >= documentHeight - 10;
    
    // Always show if page is short, hide only at bottom of long pages
    setShowBottomArrow(hasScrollableContent ? !atBottom : true);
  }, []);

  useEffect(() => {
    // Throttled scroll handler for performance
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    handleScroll(); // Initial check

    return () => window.removeEventListener('scroll', onScroll);
  }, [handleScroll]);

  // Smooth scroll to top of page
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  // Smooth scroll down by one viewport height
  const scrollDownSection = () => {
    const currentScroll = window.scrollY;
    const viewportHeight = window.innerHeight;
    
    window.scrollTo({
      top: currentScroll + viewportHeight * 0.85,
      behavior: 'smooth'
    });
  };

  const buttonClasses = `
    fixed left-1/2 -translate-x-1/2
    w-14 h-14 sm:w-16 sm:h-16
    rounded-full
    flex items-center justify-center
    cursor-pointer
    transition-all duration-300 ease-out
    focus:outline-none
    group
  `;

  return (
    <>
      {/* Top Arrow - Scroll to Top */}
      {showTopArrow && (
        <button
          onClick={scrollToTop}
          className={`
            ${buttonClasses}
            top-[100px] z-[100]
            bg-[#f5a623] hover:bg-[#d4891c]
            shadow-[0_0_20px_rgba(245,166,35,0.5)]
            hover:scale-110 hover:shadow-[0_0_30px_rgba(245,166,35,0.7)]
            animate-fade-in
          `}
          aria-label="Remonter en haut de la page"
          data-testid="scroll-nav-top"
        >
          <ChevronUp 
            className="w-8 h-8 sm:w-9 sm:h-9 text-black group-hover:-translate-y-0.5 transition-transform"
            strokeWidth={3}
          />
        </button>
      )}

      {/* Bottom Arrow - Scroll to Next Section */}
      {showBottomArrow && (
        <button
          onClick={scrollDownSection}
          className={`
            ${buttonClasses}
            bottom-6 z-[100]
            bg-[#f5a623] hover:bg-[#d4891c]
            shadow-[0_0_20px_rgba(245,166,35,0.5)]
            hover:scale-110 hover:shadow-[0_0_30px_rgba(245,166,35,0.7)]
            animate-bounce-slow
          `}
          aria-label="Défiler vers la section suivante"
          data-testid="scroll-nav-bottom"
        >
          <ChevronDown 
            className="w-8 h-8 sm:w-9 sm:h-9 text-black group-hover:translate-y-0.5 transition-transform"
            strokeWidth={3}
          />
        </button>
      )}

      {/* Animation styles */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
          to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        
        @keyframes bounce-slow {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(6px); }
        }
        
        .animate-fade-in {
          animation: fade-in 0.3s ease-out forwards;
        }
        
        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
        
        html {
          scroll-behavior: smooth;
        }
        
        /* Touch feedback on mobile */
        @media (hover: none) {
          [data-testid="scroll-nav-top"]:active,
          [data-testid="scroll-nav-bottom"]:active {
            transform: translateX(-50%) scale(0.9) !important;
          }
        }
      `}</style>
    </>
  );
};

export default ScrollNavigator;
