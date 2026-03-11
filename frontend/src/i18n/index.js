/**
 * i18n Configuration for BIONIC™
 * Centralized internationalization setup
 * 
 * Usage:
 *   import { useTranslation } from '@/i18n';
 *   const { t, language, setLanguage } = useTranslation();
 *   
 *   // Use translations
 *   <span>{t('nav.dashboard')}</span>
 *   
 *   // With nested keys
 *   <span>{t('zones.behavioral')}</span>
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

// Import locale files
import frCommon from './locales/fr/common.json';
import enCommon from './locales/en/common.json';

// Supported languages
export const SUPPORTED_LANGUAGES = {
  fr: { code: 'fr', name: 'Français', flag: '🇨🇦' },
  en: { code: 'en', name: 'English', flag: '🇬🇧' }
};

// Default language
export const DEFAULT_LANGUAGE = 'fr';

// All translations
const translations = {
  fr: { ...frCommon },
  en: { ...enCommon }
};

// i18n Context
const I18nContext = createContext(null);

/**
 * Get nested value from object using dot notation
 * @param {Object} obj - Object to search
 * @param {string} path - Dot notation path (e.g., 'nav.dashboard')
 * @returns {string} - Value or path if not found
 */
const getNestedValue = (obj, path) => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result && typeof result === 'object' && key in result) {
      result = result[key];
    } else {
      return path; // Return path if not found
    }
  }
  
  return result;
};

/**
 * i18n Provider Component
 */
export const I18nProvider = ({ children }) => {
  // Get initial language from localStorage or default
  const [language, setLanguageState] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('bionic_language');
      if (stored && SUPPORTED_LANGUAGES[stored]) {
        return stored;
      }
    }
    return DEFAULT_LANGUAGE;
  });

  // Translation function
  const t = useCallback((key, params = {}) => {
    const translation = getNestedValue(translations[language], key);
    
    if (typeof translation !== 'string') {
      console.warn(`[i18n] Missing translation for key: ${key}`);
      return key;
    }
    
    // Replace parameters {{param}}
    let result = translation;
    Object.entries(params).forEach(([param, value]) => {
      result = result.replace(new RegExp(`{{${param}}}`, 'g'), value);
    });
    
    return result;
  }, [language]);

  // Set language with persistence
  const setLanguage = useCallback((lang) => {
    if (SUPPORTED_LANGUAGES[lang]) {
      setLanguageState(lang);
      if (typeof window !== 'undefined') {
        localStorage.setItem('bionic_language', lang);
      }
      // Update document lang attribute
      document.documentElement.lang = lang;
    }
  }, []);

  // Set document lang on mount
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const value = {
    language,
    setLanguage,
    t,
    languages: SUPPORTED_LANGUAGES,
    isRTL: false // French and English are LTR
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

/**
 * Hook to use translations
 * @returns {Object} - { t, language, setLanguage, languages, isRTL }
 */
export const useTranslation = () => {
  const context = useContext(I18nContext);
  
  if (!context) {
    throw new Error('useTranslation must be used within an I18nProvider');
  }
  
  return context;
};

/**
 * Language Selector Component
 */
export const LanguageSelector = ({ className = '' }) => {
  const { language, setLanguage, languages } = useTranslation();
  
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {Object.entries(languages).map(([code, lang]) => (
        <button
          key={code}
          onClick={() => setLanguage(code)}
          className={`
            px-2 py-1 rounded text-sm font-medium transition-colors
            ${language === code 
              ? 'bg-bionic-gold text-black' 
              : 'text-gray-400 hover:text-white hover:bg-white/10'
            }
          `}
          title={lang.name}
        >
          {lang.flag} {code.toUpperCase()}
        </button>
      ))}
    </div>
  );
};

// Export default for convenience
export default {
  I18nProvider,
  useTranslation,
  LanguageSelector,
  SUPPORTED_LANGUAGES,
  DEFAULT_LANGUAGE
};
