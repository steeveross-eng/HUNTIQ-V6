import { useCallback } from 'react';
import {
  HeroSection,
  ProductCarousel,
  MapModule,
  WeatherModule,
  BentoGridSection,
  MediaFormationsSection,
  LiveStatsSection,
  MarketplaceSection,
  PartnersSection,
  BlogSection,
  CommunitySection,
  MobileAppSection,
  NewsletterSection,
  FooterSection
} from '@/components/frontpage';

/**
 * BIONIC HUNT/Chasse V3 - BIONIC™ Frontpage
 * 
 * Complete frontpage with 19 modules:
 * 1. Hero Section - Immersive hero with parallax
 * 2. Product Carousel - Featured products slider
 * 3. Map Module - Interactive Quebec territory map
 * 4. Weather Module - Real-time weather & hunting conditions
 * 5-8. Bento Grid - Terrain analysis, Species, AI Hunting, Territories
 * 9. Marketplace - Featured products grid
 * 10-11. Media & Formations - Hunt TV + Training courses
 * 12-13. Live Stats - Real-time statistics & alerts ticker
 * 14. Partners - Partners logos & featured pourvoiries
 * 15. Blog - Latest articles and SEO content
 * 16. Community - User photos & leaderboard
 * 17. Mobile App - App promotion section
 * 18. Newsletter - Email subscription
 * 19. Footer - Complete sitemap footer
 */

const BionicHomePage = ({ onAddToCart }) => {
  return (
    <main className="min-h-screen bg-[#0a0a0a]" data-testid="bionic-homepage">
      {/* 1. Hero Section - Immersive full-screen hero with BIONIC™ Stats */}
      <HeroSection />
      
      {/* 2. Product Carousel - Featured products slider */}
      <ProductCarousel onAddToCart={onAddToCart} />
      
      {/* 3. Map Module - Interactive Quebec territory map */}
      <MapModule />
      
      {/* 4. Weather Module - Real-time weather & hunting score */}
      <WeatherModule />
      
      {/* 5-8. Bento Grid Section - Analysis, Species, AI, Territories */}
      <BentoGridSection />
      
      {/* 9. Marketplace Section - E-commerce products */}
      <MarketplaceSection />
      
      {/* 10-11. Media & Formations - Hunt TV + Courses */}
      <MediaFormationsSection />
      
      {/* 12-13. Live Stats & Alerts Ticker */}
      <LiveStatsSection />
      
      {/* 14. Partners & Pourvoiries */}
      <PartnersSection />
      
      {/* 15. Blog / SEO Articles */}
      <BlogSection />
      
      {/* 16. Community Section */}
      <CommunitySection />
      
      {/* 17. Mobile App Promotion */}
      <MobileAppSection />
      
      {/* 18. Newsletter Subscription */}
      <NewsletterSection />
      
      {/* 19. Footer - Mega footer with sitemap */}
      <FooterSection />
    </main>
  );
};

export default BionicHomePage;
