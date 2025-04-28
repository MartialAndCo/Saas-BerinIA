/**
 * Page de connexion
 *
 * Cette page permet aux utilisateurs de se connecter à l'application.
 * Elle utilise le hook useAuth pour gérer l'authentification.
 */

"use client"

import dynamic from 'next/dynamic';

// Charger le composant Login dynamiquement, sans SSR
const LoginComponent = dynamic(
  () => import('@/src/components/Login'),
  { ssr: false }
);

export default function LoginPage() {
  return <LoginComponent />;
}
