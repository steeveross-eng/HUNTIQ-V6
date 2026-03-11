/**
 * OfflineService - PWA Offline functionality
 * Phase P3.4 - Mode Hors Ligne
 */

const DB_NAME = 'huntiq-offline';
const DB_VERSION = 1;

class OfflineServiceClass {
  constructor() {
    this.db = null;
    this.isOnline = navigator.onLine;
    this.listeners = [];
    
    // Listen to online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
  }

  // Initialize IndexedDB
  async init() {
    if (this.db) return this.db;
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Store for pending actions (to sync when online)
        if (!db.objectStoreNames.contains('pending-actions')) {
          db.createObjectStore('pending-actions', { keyPath: 'id', autoIncrement: true });
        }
        
        // Store for cached API data
        if (!db.objectStoreNames.contains('cached-data')) {
          db.createObjectStore('cached-data', { keyPath: 'key' });
        }
        
        // Store for waypoints
        if (!db.objectStoreNames.contains('waypoints')) {
          db.createObjectStore('waypoints', { keyPath: 'id' });
        }
        
        // Store for WQS scores
        if (!db.objectStoreNames.contains('wqs-scores')) {
          db.createObjectStore('wqs-scores', { keyPath: 'waypoint_id' });
        }
      };
    });
  }

  // Handle coming online
  async handleOnline() {
    console.log('[Offline] Back online');
    this.isOnline = true;
    this.notifyListeners('online');
    
    // Trigger background sync
    if ('serviceWorker' in navigator && 'sync' in window.SyncManager) {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('sync-waypoints');
    } else {
      // Fallback: sync manually
      await this.syncPendingActions();
    }
  }

  // Handle going offline
  handleOffline() {
    console.log('[Offline] Now offline');
    this.isOnline = false;
    this.notifyListeners('offline');
  }

  // Subscribe to online/offline events
  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  // Notify all listeners
  notifyListeners(status) {
    this.listeners.forEach(cb => cb(status, this.isOnline));
  }

  // Save data to IndexedDB
  async saveToCache(storeName, data) {
    await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Get data from IndexedDB
  async getFromCache(storeName, key) {
    await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Get all data from a store
  async getAllFromCache(storeName) {
    await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  // Delete from cache
  async deleteFromCache(storeName, key) {
    await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  // Queue an action for sync
  async queueAction(action) {
    await this.init();
    
    const pendingAction = {
      ...action,
      timestamp: Date.now()
    };
    
    return this.saveToCache('pending-actions', pendingAction);
  }

  // Get pending actions
  async getPendingActions() {
    return this.getAllFromCache('pending-actions');
  }

  // Sync pending actions manually
  async syncPendingActions() {
    const actions = await this.getPendingActions();
    
    for (const action of actions) {
      try {
        const response = await fetch(action.url, {
          method: action.method,
          headers: { 'Content-Type': 'application/json' },
          body: action.data ? JSON.stringify(action.data) : undefined
        });
        
        if (response.ok) {
          await this.deleteFromCache('pending-actions', action.id);
          console.log('[Offline] Synced action:', action.id);
        }
      } catch (error) {
        console.error('[Offline] Failed to sync:', action.id);
      }
    }
  }

  // Cache waypoints
  async cacheWaypoints(waypoints) {
    for (const wp of waypoints) {
      await this.saveToCache('waypoints', wp);
    }
    console.log('[Offline] Cached', waypoints.length, 'waypoints');
  }

  // Get cached waypoints
  async getCachedWaypoints() {
    return this.getAllFromCache('waypoints');
  }

  // Cache WQS scores
  async cacheWQSScores(scores) {
    for (const score of scores) {
      await this.saveToCache('wqs-scores', score);
    }
    console.log('[Offline] Cached', scores.length, 'WQS scores');
  }

  // Get cached WQS scores
  async getCachedWQSScores() {
    return this.getAllFromCache('wqs-scores');
  }

  // Check if app is online
  getOnlineStatus() {
    return this.isOnline;
  }

  // Register service worker
  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('[Offline] Service Worker registered:', registration.scope);
        return registration;
      } catch (error) {
        console.error('[Offline] Service Worker registration failed:', error);
        return null;
      }
    }
    return null;
  }
}

// Singleton instance
export const OfflineService = new OfflineServiceClass();

export default OfflineService;
