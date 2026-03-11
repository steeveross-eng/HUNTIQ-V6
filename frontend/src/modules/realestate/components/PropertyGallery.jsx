/**
 * PropertyGallery - Property image gallery
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Maximize2, X } from 'lucide-react';
import { Button } from '../../../components/ui/button';

/**
 * Property Gallery Component
 * 
 * @param {Object} props
 * @param {Array} props.images - Array of image URLs
 * @param {string} props.title - Property title for alt text
 */
const PropertyGallery = ({ 
  images = [],
  title = 'Propriété'
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const goToPrevious = () => {
    setCurrentIndex(prev => prev === 0 ? images.length - 1 : prev - 1);
  };

  const goToNext = () => {
    setCurrentIndex(prev => prev === images.length - 1 ? 0 : prev + 1);
  };

  if (images.length === 0) {
    return (
      <div className="h-64 bg-[var(--bionic-bg-hover)] rounded-lg flex items-center justify-center">
        <p className="text-[var(--bionic-text-muted)]">Aucune image disponible</p>
      </div>
    );
  }

  return (
    <>
      <div className="relative rounded-lg overflow-hidden">
        {/* Main Image */}
        <div className="h-64 bg-[var(--bionic-bg-hover)]">
          <img 
            src={images[currentIndex]} 
            alt={`${title} - Image ${currentIndex + 1}`}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
              onClick={goToPrevious}
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
              onClick={goToNext}
            >
              <ChevronRight className="w-5 h-5" />
            </Button>
          </>
        )}

        {/* Fullscreen Button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 bg-black/50 hover:bg-black/70 text-white"
          onClick={() => setIsFullscreen(true)}
        >
          <Maximize2 className="w-4 h-4" />
        </Button>

        {/* Counter */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/70 text-white text-xs px-2 py-1 rounded">
          {currentIndex + 1} / {images.length}
        </div>
      </div>

      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="flex gap-2 mt-2 overflow-x-auto pb-2">
          {images.map((img, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`w-16 h-12 flex-shrink-0 rounded overflow-hidden border-2 transition-colors ${
                idx === currentIndex 
                  ? 'border-[var(--bionic-gold-primary)]' 
                  : 'border-transparent'
              }`}
            >
              <img src={img} alt={`Thumbnail ${idx + 1}`} className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 text-white hover:bg-white/20"
            onClick={() => setIsFullscreen(false)}
          >
            <X className="w-6 h-6" />
          </Button>
          
          <img 
            src={images[currentIndex]} 
            alt={`${title} - Image ${currentIndex + 1}`}
            className="max-w-full max-h-full object-contain"
          />

          {images.length > 1 && (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20"
                onClick={goToPrevious}
              >
                <ChevronLeft className="w-8 h-8" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20"
                onClick={goToNext}
              >
                <ChevronRight className="w-8 h-8" />
              </Button>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default PropertyGallery;
