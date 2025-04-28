# BerinIA SAAS - Landing Page

## Description du projet
BerinIA est une plateforme SAAS (Software as a Service) qui propose des solutions d'automatisation basées sur l'intelligence artificielle pour les entreprises. Le projet comprend une landing page moderne et responsive, ainsi que des pages d'authentification (login/signup) et un tableau de bord d'administration.

## Fonctionnalités principales

### Landing Page
- Design moderne avec dégradés et animations subtiles
- Section hero avec titre accrocheur et illustration interactive
- Présentation des fonctionnalités principales
- Section de cas d'usage concrets par secteur d'activité
- Témoignages clients
- Section FAQ
- Présentation des partenaires technologiques
- Call-to-action (CTA) pour la conversion

### Pages d'authentification
- Formulaire de connexion
- Formulaire d'inscription en plusieurs étapes
- Authentification sociale (Google, Microsoft)
- Animations de transition

### Tableau de bord d'administration
- Vue d'ensemble des performances
- Gestion des campagnes
- Gestion des agents IA
- Analyse des niches de marché
- Suivi des leads
- Statistiques et rapports
- Logs et sécurité
- Paramètres système

## Modifications récentes

### Suppression de l'effet typewriter (machine à écrire)
- L'animation de type "machine à écrire" a été supprimée de la section hero
- Le composant TypewriterHeadline a été remplacé par un titre statique
- Le style visuel (dégradé de couleur) a été conservé pour maintenir l'impact visuel
- Le texte est maintenant immédiatement visible et lisible dès le chargement de la page
- Structure du titre : "Automatisez votre" (texte normal) + "entreprise avec l'IA" (avec dégradé)

## Structure du projet

### Répertoires principaux
- `/app` : Pages principales de l'application (Next.js App Router)
  - `/app/page.tsx` : Landing page
  - `/app/login` : Page de connexion
  - `/app/signup` : Page d'inscription
  - `/app/dashboard` : Tableau de bord d'administration
- `/components` : Composants réutilisables
  - `/components/ui` : Composants UI de base (shadcn/ui)
  - `/components/dashboard` : Composants spécifiques au tableau de bord
- `/public` : Ressources statiques (images, logos)
- `/hooks` : Hooks React personnalisés

### Technologies utilisées
- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS
- shadcn/ui (composants)
- Lucide React (icônes)
- Recharts (graphiques)

## Personnalisation

Le projet utilise Tailwind CSS pour le styling, ce qui permet une personnalisation facile :
- Les couleurs principales sont définies dans `tailwind.config.ts`
- Les animations sont définies dans les keyframes de Tailwind
- La police principale est Lato (importée via Google Fonts)

## Optimisations
- Composants React optimisés avec useCallback et useMemo
- Images optimisées pour le web
- Chargement paresseux (lazy loading) des composants lourds
- Design responsive pour tous les appareils
