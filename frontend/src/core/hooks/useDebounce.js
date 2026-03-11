/**
 * useDebounce - Core Hook
 * ========================
 * Hook for debouncing values (search inputs, API calls, etc.)
 * Architecture LEGO V5 - Core Hook (no business logic)
 * 
 * @module core/hooks
 */
import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * useDebounce - Debounce a value
 * @param {any} value - Value to debounce
 * @param {number} delay - Delay in ms
 */
export const useDebounce = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * useDebouncedCallback - Debounce a callback function
 * @param {Function} callback - Function to debounce
 * @param {number} delay - Delay in ms
 */
export const useDebouncedCallback = (callback, delay = 300) => {
  const timeoutRef = useRef(null);

  const debouncedCallback = useCallback((...args) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return debouncedCallback;
};

/**
 * useThrottle - Throttle a value
 * @param {any} value - Value to throttle
 * @param {number} limit - Limit in ms
 */
export const useThrottle = (value, limit = 300) => {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
};

export default useDebounce;
