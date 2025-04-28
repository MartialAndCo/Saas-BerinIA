/**
 * Configuration globale de l'application frontend
 */

// URL de base de l'API
export const API_BASE_URL = 'https://app.berinia.com/api';

// Configuration des endpoints API
export const API_ENDPOINTS = {
  // Authentification
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  
  // Niches
  NICHES: `${API_BASE_URL}/api/niches`,
  
  // Leads
  LEADS: `${API_BASE_URL}/api/leads`,
  
  // Agents
  AGENTS: `${API_BASE_URL}/api/agents`,
  
  // Campagnes
  CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
  
  // Dashboard
  DASHBOARD: `${API_BASE_URL}/api/dashboard`,
};

// Configuration des timeouts des requêtes
export const REQUEST_TIMEOUT = 30000; // 30 secondes

// Configuration des headers par défaut
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// Forcer l'utilisation des données réelles (pas de mock)
export const USE_REAL_DATA = true; 