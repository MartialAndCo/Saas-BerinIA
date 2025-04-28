import { API_ENDPOINTS, DEFAULT_HEADERS, REQUEST_TIMEOUT } from '../config';

/**
 * Service pour effectuer des requêtes API
 */
class ApiService {
  /**
   * Effectue une requête GET
   * @param {string} endpoint - L'endpoint à appeler
   * @param {Object} options - Options supplémentaires
   * @returns {Promise} - Promesse avec les données de réponse
   */
  async get(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      ...DEFAULT_HEADERS,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
    
    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        headers,
        signal: controller.signal,
        ...options,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
  
  /**
   * Effectue une requête POST
   * @param {string} endpoint - L'endpoint à appeler
   * @param {Object} data - Les données à envoyer
   * @param {Object} options - Options supplémentaires
   * @returns {Promise} - Promesse avec les données de réponse
   */
  async post(endpoint, data, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      ...DEFAULT_HEADERS,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
        signal: controller.signal,
        ...options,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
  
  // Méthodes spécifiques pour chaque ressource
  
  // Niches
  async getNiches() {
    return this.get(API_ENDPOINTS.NICHES);
  }
  
  async createNiche(data) {
    return this.post(API_ENDPOINTS.NICHES, data);
  }
  
  async getNicheById(id) {
    return this.get(`${API_ENDPOINTS.NICHES}/${id}`);
  }
  
  // Leads
  async getLeads() {
    return this.get(API_ENDPOINTS.LEADS);
  }
  
  // Autres méthodes pour les autres ressources...
}

// Exporter une instance unique du service
export default new ApiService(); 