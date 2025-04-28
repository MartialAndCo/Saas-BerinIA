import axios from 'axios'
import { API_BASE_URL } from '@/src/config' // config.js bien pris en charge même si importé en .ts

// ✅ Instance axios avec baseURL corrigée
export const api = axios.create({
  baseURL: API_BASE_URL, // doit être https://app.berinia.com/api
  headers: {
    'Content-Type': 'application/json',
  },
})

// Fonction pour obtenir le token (sans utiliser useAuth directement)
const getAuthToken = async () => {
  // Vérifier si window est défini (côté client uniquement)
  if (typeof window !== 'undefined') {
    try {
      // Récupérer le token depuis localStorage ou sessionStorage
      const token = localStorage.getItem('auth0_token');
      if (token) return token;
      
      // Si pas de token stocké, vérifier si Auth0 est disponible
      if (window.auth0Client) {
        const token = await window.auth0Client.getTokenSilently();
        localStorage.setItem('auth0_token', token);
        return token;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
  }
  return null;
};

// ✅ Intercepteur de requête pour ajouter le token
api.interceptors.request.use(
  async (config) => {
    const token = await getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
)

// ✅ Intercepteur de réponse
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Rediriger vers la page de login
      window.location.href = '/';
    }
    return Promise.reject(error)
  }
)

// ✅ Utilitaire de requête (Axios uniquement)
export const apiRequest = async (url: string, options = {}) => {
  try {
    const response = await api.get(url, options);
    return response.data;
  } catch (error) {
    console.error(`API request error for ${url}:`, error);
    throw error;
  }
}

// Types (facultatif si tu veux garder en .ts)
export interface ApiResponse<T> {
  data: T
  status: number
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}
