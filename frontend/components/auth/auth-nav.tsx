"use client"

import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';

export function AuthNav() {
  const { isAuthenticated, login, logout, user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Chargement...</div>;
  }

  return (
    <div className="flex items-center gap-4">
      {isAuthenticated ? (
        <>
          <span className="text-sm">Bonjour, {user?.name}</span>
          <Button variant="outline" onClick={() => logout()}>
            Déconnexion
          </Button>
        </>
      ) : (
        <Button onClick={() => login()}>
          Connexion
        </Button>
      )}
    </div>
  );
} 