/**
 * useZoneCache.js — Module CACHE PERSISTANT (IndexedDB)
 * 
 * CONTRAT:
 *   Input:  cacheKey (string), zones data (object)
 *   Output: cached zones or null
 * 
 * NORME BIONIC V5 300%:
 *   - Zéro lien avec le calcul backend ou le preview
 *   - Zéro mutation silencieuse
 *   - Invalidation automatique si clé change
 */
import { useCallback, useRef } from 'react';

const DB_NAME = 'bionic_zone_cache';
const DB_VERSION = 1;
const STORE_NAME = 'zones';
const MAX_ENTRIES = 50;

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'key' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getFromDB(key) {
  try {
    const db = await openDB();
    return new Promise((resolve) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result?.data || null);
      req.onerror = () => resolve(null);
    });
  } catch {
    return null;
  }
}

async function saveToDB(key, data) {
  try {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    store.put({ key, data, timestamp: Date.now() });
    // Evict old entries if over limit
    const countReq = store.count();
    countReq.onsuccess = () => {
      if (countReq.result > MAX_ENTRIES) {
        const cursor = store.openCursor();
        let deleted = 0;
        const toDelete = countReq.result - MAX_ENTRIES;
        cursor.onsuccess = (e) => {
          const c = e.target.result;
          if (c && deleted < toDelete) {
            c.delete();
            deleted++;
            c.continue();
          }
        };
      }
    };
  } catch {
    // Silent fail — cache is non-critical
  }
}

export function useZoneCache() {
  const cacheRef = useRef(new Map());

  const getCached = useCallback(async (key) => {
    if (!key) return null;
    // Memory cache first (instant)
    if (cacheRef.current.has(key)) return cacheRef.current.get(key);
    // IndexedDB second (<100ms)
    const data = await getFromDB(key);
    if (data) cacheRef.current.set(key, data);
    return data;
  }, []);

  const setCached = useCallback(async (key, data) => {
    if (!key || !data) return;
    cacheRef.current.set(key, data);
    await saveToDB(key, data);
  }, []);

  const invalidate = useCallback(async (key) => {
    if (!key) return;
    cacheRef.current.delete(key);
    try {
      const db = await openDB();
      const tx = db.transaction(STORE_NAME, 'readwrite');
      tx.objectStore(STORE_NAME).delete(key);
    } catch { /* silent */ }
  }, []);

  return { getCached, setCached, invalidate };
}
