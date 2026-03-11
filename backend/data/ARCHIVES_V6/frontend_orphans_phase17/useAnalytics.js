/**
 * Analytics Hook
 * Track page views, clicks, conversions, etc.
 */

import { useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Generate or retrieve session ID
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('bionic_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('bionic_session_id', sessionId);
  }
  return sessionId;
};

// Get user ID from localStorage if available
const getUserId = () => {
  return localStorage.getItem('territory_user_id') || 
         localStorage.getItem('marketplace_auth')?.seller?.id ||
         null;
};

export const useAnalytics = () => {
  const location = useLocation();

  // Track page view on route change
  useEffect(() => {
    trackEvent('page_view', { 
      page_title: document.title,
      referrer: document.referrer
    });
  }, [location.pathname]);

  const trackEvent = useCallback(async (eventType, metadata = {}) => {
    try {
      await axios.post(`${API}/seo/analytics/track`, {
        event_type: eventType,
        page_url: location.pathname,
        user_id: getUserId(),
        session_id: getSessionId(),
        metadata: {
          ...metadata,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          screen_size: `${window.innerWidth}x${window.innerHeight}`
        }
      });
    } catch (error) {
      // Silent fail - don't break the app for analytics
      console.debug('Analytics tracking failed:', error);
    }
  }, [location.pathname]);

  const trackClick = useCallback((elementId, metadata = {}) => {
    trackEvent('click', { element_id: elementId, ...metadata });
  }, [trackEvent]);

  const trackConversion = useCallback((conversionType, value, metadata = {}) => {
    trackEvent('conversion', { 
      conversion_type: conversionType, 
      value,
      ...metadata 
    });
  }, [trackEvent]);

  const trackAddToCart = useCallback((productId, productName, price, quantity = 1) => {
    trackEvent('add_to_cart', {
      product_id: productId,
      product_name: productName,
      price,
      quantity
    });
  }, [trackEvent]);

  const trackVideoView = useCallback((videoId, videoTitle, duration, percentWatched = 0) => {
    trackEvent('video_view', {
      video_id: videoId,
      video_title: videoTitle,
      duration,
      percent_watched: percentWatched
    });
  }, [trackEvent]);

  const trackSearch = useCallback((query, resultsCount) => {
    trackEvent('search', {
      query,
      results_count: resultsCount
    });
  }, [trackEvent]);

  return {
    trackEvent,
    trackClick,
    trackConversion,
    trackAddToCart,
    trackVideoView,
    trackSearch
  };
};

export default useAnalytics;
