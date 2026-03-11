/**
 * PHASE G — CORE MODULE (Orchestrateur)
 * 
 * Module central qui orchestre tous les modules PHASE G.
 * Gère l'isolation, la sécurité et l'audit de tous les appels.
 * 
 * @module phase-g/core
 * @version G-CORE-v1.0.0
 * @phase G-P0
 * @security G-SEC compliant
 */

// ============================================
// CONFIGURATION
// ============================================

const CORE_CONFIG = {
  version: '1.0.0',
  modulePrefix: 'G-',
  auditEnabled: true,
  sandboxEnabled: true,
  maxExecutionTime: 30000, // ms
  logLevel: 'info' // 'debug', 'info', 'warn', 'error'
};

// ============================================
// REGISTRY DES MODULES
// ============================================

const moduleRegistry = new Map();
const moduleMetrics = new Map();

/**
 * Enregistre un module dans le core
 * @param {string} moduleId - Identifiant unique du module
 * @param {object} moduleInstance - Instance du module
 * @param {object} contract - Contrat d'API du module
 */
export const registerModule = (moduleId, moduleInstance, contract) => {
  if (!moduleId.startsWith(CORE_CONFIG.modulePrefix)) {
    throw new Error(`[G-SEC] Module ID must start with '${CORE_CONFIG.modulePrefix}'`);
  }
  
  if (moduleRegistry.has(moduleId)) {
    throw new Error(`[G-SEC] Module '${moduleId}' already registered`);
  }
  
  // Validation du contrat
  if (!contract || !contract.version || !contract.methods) {
    throw new Error(`[G-SEC] Invalid contract for module '${moduleId}'`);
  }
  
  // Création du wrapper sécurisé
  const secureModule = createSecureWrapper(moduleId, moduleInstance, contract);
  
  moduleRegistry.set(moduleId, {
    instance: secureModule,
    contract,
    registeredAt: new Date(),
    status: 'active'
  });
  
  // Initialisation des métriques
  moduleMetrics.set(moduleId, {
    calls: 0,
    errors: 0,
    avgResponseTime: 0,
    lastCall: null
  });
  
  logAudit('MODULE_REGISTERED', { moduleId, version: contract.version });
  
  return secureModule;
};

/**
 * Crée un wrapper sécurisé autour d'un module
 */
const createSecureWrapper = (moduleId, instance, contract) => {
  const wrapper = {};
  
  for (const [methodName, methodDef] of Object.entries(contract.methods)) {
    wrapper[methodName] = async (...args) => {
      const startTime = performance.now();
      const callId = generateCallId();
      
      try {
        // Logging d'entrée
        logAudit('METHOD_CALL_START', {
          callId,
          moduleId,
          method: methodName,
          args: sanitizeForLog(args)
        });
        
        // Validation des entrées
        validateInput(args[0], methodDef.input);
        
        // Exécution avec timeout
        const result = await executeWithTimeout(
          () => instance[methodName](...args),
          CORE_CONFIG.maxExecutionTime
        );
        
        // Validation de la sortie
        validateOutput(result, methodDef.output, contract.outputTypes);
        
        // Mise à jour des métriques
        updateMetrics(moduleId, performance.now() - startTime, false);
        
        // Logging de sortie
        logAudit('METHOD_CALL_SUCCESS', {
          callId,
          moduleId,
          method: methodName,
          duration: performance.now() - startTime
        });
        
        return result;
        
      } catch (error) {
        updateMetrics(moduleId, performance.now() - startTime, true);
        
        logAudit('METHOD_CALL_ERROR', {
          callId,
          moduleId,
          method: methodName,
          error: error.message,
          duration: performance.now() - startTime
        });
        
        // Fallback si disponible
        if (methodDef.fallback && instance[methodDef.fallback]) {
          logAudit('FALLBACK_TRIGGERED', { callId, moduleId, fallback: methodDef.fallback });
          return instance[methodDef.fallback](...args);
        }
        
        throw error;
      }
    };
  }
  
  return wrapper;
};

// ============================================
// VALIDATION
// ============================================

const validateInput = (input, schema) => {
  if (!schema) return;
  
  for (const [key, expectedType] of Object.entries(schema)) {
    const value = input?.[key];
    const types = expectedType.split('|');
    
    let valid = types.some(type => {
      if (type === 'null') return value === null;
      if (type === 'undefined') return value === undefined;
      if (type === 'number') return typeof value === 'number' && !isNaN(value);
      if (type === 'string') return typeof value === 'string';
      if (type === 'boolean') return typeof value === 'boolean';
      if (type === 'object') return typeof value === 'object' && value !== null;
      if (type === 'Date') return value instanceof Date || !isNaN(Date.parse(value));
      if (type.endsWith('[]')) return Array.isArray(value);
      return true; // Complex types validated elsewhere
    });
    
    if (!valid && !types.includes('null') && !types.includes('undefined')) {
      throw new Error(`[G-SEC] Invalid input: '${key}' expected ${expectedType}, got ${typeof value}`);
    }
  }
};

const validateOutput = (output, expectedType, outputTypes) => {
  // Basic validation - complex validation handled by module tests
  if (output === null || output === undefined) {
    if (!expectedType.includes('null')) {
      throw new Error(`[G-SEC] Invalid output: expected ${expectedType}, got null`);
    }
  }
};

// ============================================
// UTILITAIRES
// ============================================

const generateCallId = () => {
  return `G-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const executeWithTimeout = (fn, timeout) => {
  return Promise.race([
    fn(),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('[G-SEC] Execution timeout')), timeout)
    )
  ]);
};

const sanitizeForLog = (data) => {
  // Remove sensitive data before logging
  if (typeof data !== 'object') return data;
  const sanitized = JSON.parse(JSON.stringify(data));
  // Add sanitization rules as needed
  return sanitized;
};

const updateMetrics = (moduleId, duration, isError) => {
  const metrics = moduleMetrics.get(moduleId);
  if (!metrics) return;
  
  metrics.calls++;
  if (isError) metrics.errors++;
  metrics.avgResponseTime = (metrics.avgResponseTime * (metrics.calls - 1) + duration) / metrics.calls;
  metrics.lastCall = new Date();
  
  moduleMetrics.set(moduleId, metrics);
};

// ============================================
// AUDIT LOGGING
// ============================================

const auditLog = [];
const MAX_AUDIT_LOG = 10000;

const logAudit = (event, data) => {
  if (!CORE_CONFIG.auditEnabled) return;
  
  const entry = {
    timestamp: new Date().toISOString(),
    event,
    data,
    level: getLogLevel(event)
  };
  
  auditLog.push(entry);
  
  // Rotation du log
  if (auditLog.length > MAX_AUDIT_LOG) {
    auditLog.shift();
  }
  
  // Console logging based on level
  if (CORE_CONFIG.logLevel === 'debug' || 
      (CORE_CONFIG.logLevel === 'info' && entry.level !== 'debug') ||
      (CORE_CONFIG.logLevel === 'warn' && ['warn', 'error'].includes(entry.level)) ||
      (CORE_CONFIG.logLevel === 'error' && entry.level === 'error')) {
    console.log(`[G-AUDIT] ${entry.timestamp} ${event}`, data);
  }
};

const getLogLevel = (event) => {
  if (event.includes('ERROR')) return 'error';
  if (event.includes('WARN') || event.includes('FALLBACK')) return 'warn';
  if (event.includes('START') || event.includes('REGISTERED')) return 'debug';
  return 'info';
};

// ============================================
// API PUBLIQUE
// ============================================

/**
 * Récupère un module enregistré
 */
export const getModule = (moduleId) => {
  const module = moduleRegistry.get(moduleId);
  if (!module) {
    throw new Error(`[G-SEC] Module '${moduleId}' not found`);
  }
  return module.instance;
};

/**
 * Vérifie si un module est enregistré
 */
export const hasModule = (moduleId) => {
  return moduleRegistry.has(moduleId);
};

/**
 * Récupère les métriques d'un module
 */
export const getModuleMetrics = (moduleId) => {
  return moduleMetrics.get(moduleId) || null;
};

/**
 * Récupère toutes les métriques
 */
export const getAllMetrics = () => {
  const metrics = {};
  for (const [moduleId, data] of moduleMetrics) {
    metrics[moduleId] = { ...data };
  }
  return metrics;
};

/**
 * Récupère le log d'audit
 */
export const getAuditLog = (limit = 100) => {
  return auditLog.slice(-limit);
};

/**
 * Réinitialise les métriques (pour tests)
 */
export const resetMetrics = () => {
  for (const moduleId of moduleMetrics.keys()) {
    moduleMetrics.set(moduleId, {
      calls: 0,
      errors: 0,
      avgResponseTime: 0,
      lastCall: null
    });
  }
};

/**
 * Configuration du core
 */
export const configure = (config) => {
  Object.assign(CORE_CONFIG, config);
  logAudit('CORE_CONFIGURED', { config });
};

/**
 * Retourne la configuration actuelle
 */
export const getConfig = () => ({ ...CORE_CONFIG });

/**
 * Retourne la version du core
 */
export const getVersion = () => CORE_CONFIG.version;

export default {
  registerModule,
  getModule,
  hasModule,
  getModuleMetrics,
  getAllMetrics,
  getAuditLog,
  resetMetrics,
  configure,
  getConfig,
  getVersion
};
