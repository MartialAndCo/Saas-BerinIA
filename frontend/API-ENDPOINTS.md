# API Endpoints BerinIA

Ce document liste tous les endpoints API nécessaires pour le fonctionnement de l'application BerinIA. Ces endpoints sont regroupés par fonctionnalité pour faciliter la priorisation du développement backend.

## Authentification

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/auth/login` | POST | Authentification d'un utilisateur | Haute |
| `/api/auth/register` | POST | Création d'un nouveau compte | Haute |
| `/api/auth/logout` | POST | Déconnexion de l'utilisateur | Haute |
| `/api/auth/refresh` | POST | Rafraîchissement du token d'authentification | Haute |
| `/api/auth/password/reset` | POST | Demande de réinitialisation de mot de passe | Moyenne |
| `/api/auth/password/update` | PUT | Mise à jour du mot de passe | Moyenne |
| `/api/auth/me` | GET | Récupération des informations de l'utilisateur connecté | Haute |

## Campagnes

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/campaigns` | GET | Liste des campagnes | Haute |
| `/api/campaigns` | POST | Création d'une nouvelle campagne | Haute |
| `/api/campaigns/:id` | GET | Détails d'une campagne spécifique | Haute |
| `/api/campaigns/:id` | PUT | Mise à jour d'une campagne | Haute |
| `/api/campaigns/:id` | DELETE | Suppression d'une campagne | Moyenne |
| `/api/campaigns/:id/status` | PUT | Mise à jour du statut d'une campagne (activer/désactiver) | Haute |
| `/api/campaigns/:id/stats` | GET | Statistiques d'une campagne | Moyenne |

## Leads

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/leads` | GET | Liste des leads | Haute |
| `/api/leads` | POST | Création d'un nouveau lead | Haute |
| `/api/leads/:id` | GET | Détails d'un lead spécifique | Haute |
| `/api/leads/:id` | PUT | Mise à jour d'un lead | Haute |
| `/api/leads/:id` | DELETE | Suppression d'un lead | Basse |
| `/api/leads/export` | GET | Export des leads (CSV/Excel) | Moyenne |
| `/api/leads/import` | POST | Import des leads | Basse |
| `/api/leads/status/:status` | GET | Filtrage des leads par statut | Moyenne |

## Agents IA

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/agents` | GET | Liste des agents IA | Haute |
| `/api/agents` | POST | Création d'un nouvel agent | Haute |
| `/api/agents/:id` | GET | Détails d'un agent spécifique | Haute |
| `/api/agents/:id` | PUT | Mise à jour d'un agent | Haute |
| `/api/agents/:id` | DELETE | Suppression d'un agent | Moyenne |
| `/api/agents/:id/status` | PUT | Mise à jour du statut d'un agent (activer/désactiver) | Haute |
| `/api/agents/:id/restart` | POST | Redémarrage d'un agent en erreur | Haute |
| `/api/agents/:id/logs` | GET | Logs d'un agent spécifique | Moyenne |

## Niches

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/niches` | GET | Liste des niches | Haute |
| `/api/niches` | POST | Création d'une nouvelle niche | Haute |
| `/api/niches/:id` | GET | Détails d'une niche spécifique | Haute |
| `/api/niches/:id` | PUT | Mise à jour d'une niche | Haute |
| `/api/niches/:id` | DELETE | Suppression d'une niche | Moyenne |
| `/api/niches/:id/stats` | GET | Statistiques d'une niche | Moyenne |
| `/api/niches/:id/recommendations` | GET | Recommandations pour une niche | Moyenne |

## Statistiques et Analytics

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/stats/overview` | GET | Vue d'ensemble des statistiques | Haute |
| `/api/stats/campaigns` | GET | Statistiques des campagnes | Haute |
| `/api/stats/leads` | GET | Statistiques des leads | Haute |
| `/api/stats/niches` | GET | Statistiques des niches | Haute |
| `/api/stats/conversion` | GET | Taux de conversion | Haute |
| `/api/stats/period/:period` | GET | Statistiques pour une période spécifique | Moyenne |

## Logs et Sécurité

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/logs` | GET | Liste des logs système | Moyenne |
| `/api/logs/auth` | GET | Logs d'authentification | Moyenne |
| `/api/logs/agents` | GET | Logs des agents | Moyenne |
| `/api/logs/errors` | GET | Logs d'erreurs | Moyenne |
| `/api/security/api-keys` | GET | Liste des clés API | Basse |
| `/api/security/api-keys` | POST | Création d'une nouvelle clé API | Basse |
| `/api/security/api-keys/:id` | DELETE | Révocation d'une clé API | Basse |

## Utilisateurs et Permissions

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/users` | GET | Liste des utilisateurs | Moyenne |
| `/api/users` | POST | Création d'un nouvel utilisateur | Moyenne |
| `/api/users/:id` | GET | Détails d'un utilisateur spécifique | Moyenne |
| `/api/users/:id` | PUT | Mise à jour d'un utilisateur | Moyenne |
| `/api/users/:id` | DELETE | Suppression d'un utilisateur | Basse |
| `/api/users/:id/status` | PUT | Activation/désactivation d'un utilisateur | Moyenne |
| `/api/roles` | GET | Liste des rôles | Basse |
| `/api/permissions` | GET | Liste des permissions | Basse |

## Paramètres

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/settings/general` | GET | Paramètres généraux | Moyenne |
| `/api/settings/general` | PUT | Mise à jour des paramètres généraux | Moyenne |
| `/api/settings/integrations` | GET | Paramètres d'intégration | Moyenne |
| `/api/settings/integrations` | PUT | Mise à jour des paramètres d'intégration | Moyenne |
| `/api/settings/notifications` | GET | Paramètres de notification | Basse |
| `/api/settings/notifications` | PUT | Mise à jour des paramètres de notification | Basse |
| `/api/settings/scheduling` | GET | Paramètres de planification | Basse |
| `/api/settings/scheduling` | PUT | Mise à jour des paramètres de planification | Basse |

## Webhooks

| Endpoint | Méthode | Description | Priorité |
|----------|---------|-------------|----------|
| `/api/webhooks/leads` | POST | Webhook pour les nouveaux leads | Basse |
| `/api/webhooks/campaigns` | POST | Webhook pour les changements de statut des campagnes | Basse |
