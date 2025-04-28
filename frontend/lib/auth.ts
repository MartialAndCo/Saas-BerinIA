import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';
import { authStorage } from './auth-storage';

export const useAuth = () => {
  const {
    isAuthenticated,
    loginWithRedirect,
    logout: auth0Logout,
    user,
    getAccessTokenSilently,
    isLoading
  } = useAuth0();

  // Stocker le token et l'utilisateur dans le localStorage
  useEffect(() => {
    const storeAuthData = async () => {
      if (isAuthenticated && user) {
        try {
          // Stocker l'utilisateur
          authStorage.setUser(user);
          
          // Obtenir et stocker le token
          const token = await getAccessTokenSilently();
          authStorage.setToken(token);
          
          // Définir un cookie pour le middleware
          document.cookie = `auth0.is.authenticated=true; path=/; max-age=${60 * 60 * 24}; SameSite=Lax`;
        } catch (error) {
          console.error('Error storing auth data:', error);
        }
      }
    };

    if (isAuthenticated && user) {
      storeAuthData();
    }
  }, [isAuthenticated, user, getAccessTokenSilently]);

  // Fonction de déconnexion améliorée
  const logout = () => {
    // Supprimer les données stockées
    authStorage.clearAuth();
    
    // Supprimer le cookie
    document.cookie = 'auth0.is.authenticated=; path=/; max-age=0; SameSite=Lax';
    
    // Déconnexion Auth0
    auth0Logout({ 
      logoutParams: {
        returnTo: window.location.origin 
      }
    });
  };

  return {
    isAuthenticated,
    isLoading,
    user,
    login: loginWithRedirect,
    logout,
    getToken: getAccessTokenSilently
  };
}; 