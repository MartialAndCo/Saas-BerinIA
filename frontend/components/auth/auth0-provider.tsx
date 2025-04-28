"use client";

import { Auth0Provider } from "@auth0/auth0-react";
import React, { useEffect } from "react";

export const Auth0ProviderWithNavigate = ({ children }: { children: React.ReactNode }) => {
  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN || "";
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || "";
  const audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE || "";

  // Afficher les variables d'environnement pour déboguer (à supprimer en production)
  useEffect(() => {
    console.log("Auth0 Config:", { 
      domain, 
      clientId, 
      audience,
      origin: typeof window !== "undefined" ? window.location.origin : ""
    });
  }, [domain, clientId, audience]);

  const onRedirectCallback = (appState: any) => {
    console.log("Auth0 Redirect Callback:", appState);
    
    // Le callback est géré par la page auth-callback
    // Pas besoin de faire quoi que ce soit ici
  };

  if (!domain || !clientId) {
    console.error("Auth0 configuration missing");
    return <>{children}</>;
  }

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: typeof window !== "undefined" ? `${window.location.origin}/auth-callback` : "",
        audience: audience,
      }}
      cacheLocation="localstorage"
      useRefreshTokens={true}
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </Auth0Provider>
  );
}; 