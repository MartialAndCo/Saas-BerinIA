// Gestion du stockage des tokens Auth0
const AUTH0_TOKEN_KEY = 'auth0_token';
const AUTH0_USER_KEY = 'auth0_user';

// Vérifier si le code s'exécute côté client
const isClient = typeof window !== 'undefined';

export const authStorage = {
  // Stocker le token
  setToken: (token: string) => {
    if (isClient) {
      localStorage.setItem(AUTH0_TOKEN_KEY, token);
    }
  },
  
  // Récupérer le token
  getToken: (): string | null => {
    if (isClient) {
      return localStorage.getItem(AUTH0_TOKEN_KEY);
    }
    return null;
  },
  
  // Supprimer le token
  removeToken: () => {
    if (isClient) {
      localStorage.removeItem(AUTH0_TOKEN_KEY);
    }
  },
  
  // Stocker les informations utilisateur
  setUser: (user: any) => {
    if (isClient && user) {
      localStorage.setItem(AUTH0_USER_KEY, JSON.stringify(user));
    }
  },
  
  // Récupérer les informations utilisateur
  getUser: () => {
    if (isClient) {
      const userStr = localStorage.getItem(AUTH0_USER_KEY);
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch (e) {
          console.error('Error parsing user data:', e);
        }
      }
    }
    return null;
  },
  
  // Supprimer les informations utilisateur
  removeUser: () => {
    if (isClient) {
      localStorage.removeItem(AUTH0_USER_KEY);
    }
  },
  
  // Effacer toutes les données d'authentification
  clearAuth: () => {
    if (isClient) {
      localStorage.removeItem(AUTH0_TOKEN_KEY);
      localStorage.removeItem(AUTH0_USER_KEY);
    }
  }
}; 