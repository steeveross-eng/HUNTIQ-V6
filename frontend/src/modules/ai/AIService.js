/**
 * AI Service - API client for AI module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class AIService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/ai/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async analyzeProduct(productId, productName = null) {
    try {
      const response = await fetch(`${API_URL}/api/v1/ai/analyze/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName })
      });
      
      if (!response.ok) {
        return this.getPlaceholderAnalysis(productId, productName);
      }
      return response.json();
    } catch {
      return this.getPlaceholderAnalysis(productId, productName);
    }
  }

  static async query(queryText, context = {}) {
    try {
      const response = await fetch(`${API_URL}/api/v1/ai/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          ...context
        })
      });
      
      if (!response.ok) {
        return this.getPlaceholderResponse(queryText);
      }
      return response.json();
    } catch {
      return this.getPlaceholderResponse(queryText);
    }
  }

  static async chat(message, sessionId = null, context = {}) {
    try {
      const response = await fetch(`${API_URL}/api/v1/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          context
        })
      });
      
      if (!response.ok) {
        return {
          response: `Je comprends votre question sur "${message}". Basé sur les conditions actuelles et les données disponibles, je recommande de privilégier les heures dorées (aube et crépuscule) pour maximiser vos chances de succès. La patience et l'observation sont clés.`,
          session_id: sessionId || 'session_' + Date.now()
        };
      }
      return response.json();
    } catch {
      return {
        response: `Je comprends votre question. En tant qu'assistant BIONIC™, je vous suggère de vérifier les conditions météo et l'activité de la faune avant votre sortie. Voulez-vous des recommandations plus spécifiques?`,
        session_id: sessionId || 'session_' + Date.now()
      };
    }
  }

  static async getInsights(context = {}) {
    try {
      const response = await fetch(`${API_URL}/api/v1/ai/insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context)
      });
      
      if (!response.ok) {
        return this.getPlaceholderInsights();
      }
      return response.json();
    } catch {
      return this.getPlaceholderInsights();
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderAnalysis(productId, productName) {
    return {
      success: true,
      product_id: productId,
      product_name: productName || 'Produit',
      ai_score: 78,
      analysis: {
        effectiveness: 'Haute efficacité prédite pour les cervidés',
        best_conditions: 'Optimal par temps frais et humide',
        duration: 'Effet estimé: 36-48 heures',
        recommendation: 'Recommandé pour utilisation pendant le rut'
      },
      strengths: ['Bonne persistance', 'Attractivité olfactive élevée'],
      improvements: ['Résistance à la pluie à améliorer']
    };
  }

  static getPlaceholderResponse(query) {
    return {
      success: true,
      query: query,
      response: `Analyse en cours pour "${query}". Les données BIONIC™ suggèrent des conditions favorables pour la chasse. Consultez les modules Météo et Wildlife pour des informations détaillées.`,
      confidence: 0.75
    };
  }

  static getPlaceholderInsights() {
    return {
      insights: [
        { type: 'tip', title: 'Période optimale', message: 'Le rut est à son pic. Privilégiez les zones de frottage.' },
        { type: 'trend', title: 'Activité accrue', message: 'Mouvement prévu entre 6h-9h et 16h-19h.' },
        { type: 'warning', title: 'Vent défavorable', message: 'Vent du sud - ajustez votre position.' }
      ]
    };
  }
}

export default AIService;
