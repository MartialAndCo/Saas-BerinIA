# Documentation détaillée des API Endpoints BerinIA

Ce document fournit une documentation détaillée des endpoints API de BerinIA, incluant des exemples de requêtes et réponses ainsi que les codes HTTP attendus.

## Authentification

### POST /api/auth/login

Authentifie un utilisateur et retourne un token d'accès.

**Requête:**
\`\`\`json
{
  "email": "admin@berinia.com",
  "password": "password123",
  "rememberMe": true
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "user": {
    "id": "1",
    "name": "Admin",
    "email": "admin@berinia.com",
    "role": "admin",
    "avatar": "A",
    "lastLogin": "10/06/2023 15:45",
    "status": "active"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Identifiants incorrects
- `403 Forbidden`: Compte désactivé

### POST /api/auth/register

Crée un nouveau compte utilisateur.

**Requête:**
\`\`\`json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "password": "SecurePassword123",
  "company": "Entreprise SAS",
  "jobTitle": "Directeur Marketing",
  "agreeTerms": true
}
\`\`\`

**Réponse (201 Created):**
\`\`\`json
{
  "user": {
    "id": "2",
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "role": "viewer",
    "avatar": "JD",
    "lastLogin": "15/06/2023 10:30",
    "status": "active"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides ou email déjà utilisé
- `422 Unprocessable Entity`: Validation échouée (ex: mot de passe trop faible)

### POST /api/auth/refresh

Rafraîchit le token d'authentification.

**Requête:**
\`\`\`json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Token manquant
- `401 Unauthorized`: Token invalide ou expiré

### POST /api/auth/logout

Déconnecte l'utilisateur en invalidant son token.

**Requête:**
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "message": "Déconnexion réussie"
}
\`\`\`

### GET /api/auth/me

Récupère les informations de l'utilisateur connecté.

**Requête:** Aucun corps de requête, juste le token dans l'en-tête Authorization.

**Réponse (200 OK):**
\`\`\`json
{
  "id": "1",
  "name": "Admin",
  "email": "admin@berinia.com",
  "role": "admin",
  "avatar": "A",
  "lastLogin": "10/06/2023 15:45",
  "status": "active",
  "permissions": ["campaigns.create", "campaigns.edit", "campaigns.delete", "users.manage"]
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Compte désactivé

## Campagnes

### GET /api/campaigns

Récupère la liste des campagnes avec pagination et filtrage.

**Requête:** Query parameters
\`\`\`
?page=1&limit=10&status=active&niche=Immobilier&search=Paris
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "id": 1,
      "name": "Agences immobilières Paris",
      "niche": "Immobilier",
      "status": "active",
      "leads": 342,
      "conversion": 7.8,
      "date": "01/05/2023",
      "agent": "Scraper Agent",
      "progress": 78
    },
    {
      "id": 5,
      "name": "Immobilier de luxe Paris",
      "niche": "Immobilier",
      "status": "active",
      "leads": 156,
      "conversion": 6.5,
      "date": "05/05/2023",
      "agent": "Scraper Agent",
      "progress": 62
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 10,
  "totalPages": 1
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### POST /api/campaigns

Crée une nouvelle campagne.

**Requête:**
\`\`\`json
{
  "name": "Notaires Marseille",
  "niche": "Juridique",
  "description": "Campagne ciblant les notaires de la région de Marseille",
  "targetLeads": 200,
  "agent": "Scraper Agent"
}
\`\`\`

**Réponse (201 Created):**
\`\`\`json
{
  "id": 9,
  "name": "Notaires Marseille",
  "niche": "Juridique",
  "description": "Campagne ciblant les notaires de la région de Marseille",
  "status": "active",
  "leads": 0,
  "conversion": 0,
  "date": "15/06/2023",
  "agent": "Scraper Agent",
  "progress": 0,
  "targetLeads": 200,
  "createdBy": "1"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `422 Unprocessable Entity`: Validation échouée

### GET /api/campaigns/:id

Récupère les détails d'une campagne spécifique.

**Requête:** Aucun corps de requête, juste l'ID dans l'URL.

**Réponse (200 OK):**
\`\`\`json
{
  "id": 1,
  "name": "Agences immobilières Paris",
  "niche": "Immobilier",
  "description": "Campagne ciblant les agences immobilières de Paris",
  "status": "active",
  "leads": 342,
  "conversion": 7.8,
  "date": "01/05/2023",
  "agent": "Scraper Agent",
  "progress": 78,
  "targetLeads": 500,
  "createdBy": "1",
  "createdAt": "2023-05-01T08:00:00Z",
  "updatedAt": "2023-06-10T15:30:00Z",
  "stats": {
    "leadsPerDay": [
      {"date": "2023-05-01", "count": 50},
      {"date": "2023-05-02", "count": 75},
      {"date": "2023-05-03", "count": 62}
    ],
    "conversionRate": 7.8,
    "costPerLead": 2.35
  }
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Campagne non trouvée

### PUT /api/campaigns/:id

Met à jour une campagne existante.

**Requête:**
\`\`\`json
{
  "name": "Agences immobilières Paris - Mise à jour",
  "description": "Campagne ciblant les agences immobilières de Paris et sa banlieue",
  "targetLeads": 600
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "id": 1,
  "name": "Agences immobilières Paris - Mise à jour",
  "niche": "Immobilier",
  "description": "Campagne ciblant les agences immobilières de Paris et sa banlieue",
  "status": "active",
  "leads": 342,
  "conversion": 7.8,
  "date": "01/05/2023",
  "agent": "Scraper Agent",
  "progress": 78,
  "targetLeads": 600,
  "updatedAt": "2023-06-15T10:30:00Z"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Campagne non trouvée
- `422 Unprocessable Entity`: Validation échouée

### PUT /api/campaigns/:id/status

Met à jour le statut d'une campagne (activer/désactiver).

**Requête:**
\`\`\`json
{
  "status": "paused",
  "reason": "Pause temporaire pour optimisation"
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "id": 1,
  "status": "paused",
  "updatedAt": "2023-06-15T11:45:00Z",
  "statusHistory": [
    {
      "status": "active",
      "timestamp": "2023-05-01T08:00:00Z",
      "reason": "Création de la campagne"
    },
    {
      "status": "paused",
      "timestamp": "2023-06-15T11:45:00Z",
      "reason": "Pause temporaire pour optimisation"
    }
  ]
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Statut invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Campagne non trouvée

## Leads

### GET /api/leads

Récupère la liste des leads avec pagination et filtrage.

**Requête:** Query parameters
\`\`\`
?page=1&limit=10&status=new&campaign=1&search=dupont
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "id": 1,
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "phone": "06 12 34 56 78",
      "company": "Immobilier Paris",
      "campaign": "Agences immobilières Paris",
      "campaignId": 1,
      "status": "new",
      "date": "01/06/2023"
    },
    {
      "id": 6,
      "name": "Julie Dupont",
      "email": "julie.dupont@example.com",
      "phone": "06 67 89 01 23",
      "company": "Immobilier Petit",
      "campaign": "Agences immobilières Paris",
      "campaignId": 1,
      "status": "new",
      "date": "06/06/2023"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 10,
  "totalPages": 1
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### POST /api/leads

Crée un nouveau lead.

**Requête:**
\`\`\`json
{
  "name": "Pierre Martin",
  "email": "pierre.martin@example.com",
  "phone": "06 98 76 54 32",
  "company": "Martin Immobilier",
  "campaignId": 1,
  "source": "LinkedIn",
  "notes": "Intéressé par une démo"
}
\`\`\`

**Réponse (201 Created):**
\`\`\`json
{
  "id": 11,
  "name": "Pierre Martin",
  "email": "pierre.martin@example.com",
  "phone": "06 98 76 54 32",
  "company": "Martin Immobilier",
  "campaign": "Agences immobilières Paris",
  "campaignId": 1,
  "status": "new",
  "date": "15/06/2023",
  "source": "LinkedIn",
  "notes": "Intéressé par une démo",
  "createdAt": "2023-06-15T14:30:00Z"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `422 Unprocessable Entity`: Validation échouée

### PUT /api/leads/:id/status

Met à jour le statut d'un lead.

**Requête:**
\`\`\`json
{
  "status": "qualified",
  "notes": "Lead qualifié après appel téléphonique"
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "id": 1,
  "status": "qualified",
  "updatedAt": "2023-06-15T15:20:00Z",
  "statusHistory": [
    {
      "status": "new",
      "timestamp": "2023-06-01T10:00:00Z"
    },
    {
      "status": "contacted",
      "timestamp": "2023-06-10T14:30:00Z",
      "notes": "Premier contact par email"
    },
    {
      "status": "qualified",
      "timestamp": "2023-06-15T15:20:00Z",
      "notes": "Lead qualifié après appel téléphonique"
    }
  ]
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Statut invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Lead non trouvé

### GET /api/leads/export

Exporte les leads au format CSV ou Excel.

**Requête:** Query parameters
\`\`\`
?format=csv&campaignId=1&status=all
\`\`\`

**Réponse (200 OK):**
Fichier CSV ou Excel en téléchargement.

**Erreurs:**
- `400 Bad Request`: Format invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

## Agents IA

### GET /api/agents

Récupère la liste des agents IA.

**Requête:** Query parameters
\`\`\`
?status=active
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "id": 1,
      "name": "Scraper Agent",
      "type": "Collection",
      "status": "active",
      "lastRun": "Il y a 5 minutes",
      "leads": 342,
      "campaigns": 3,
      "description": "Agent de collecte de leads",
      "configuration": {
        "maxLeadsPerRun": 100,
        "runFrequency": "daily"
      }
    },
    {
      "id": 2,
      "name": "Cleaner Agent",
      "type": "Traitement",
      "status": "active",
      "lastRun": "Il y a 12 minutes",
      "leads": 342,
      "campaigns": 3,
      "description": "Agent de nettoyage et déduplication des leads",
      "configuration": {
        "deduplicationEnabled": true,
        "emailValidationEnabled": true
      }
    }
  ],
  "total": 2
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### POST /api/agents/:id/restart

Redémarre un agent en erreur.

**Requête:**
\`\`\`json
{
  "force": true,
  "reason": "Résolution du problème d'API timeout"
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "id": 4,
  "name": "Analytics Agent",
  "status": "active",
  "lastRun": "À l'instant",
  "message": "Agent redémarré avec succès",
  "previousStatus": "error",
  "restartedAt": "2023-06-15T16:45:00Z"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Agent déjà actif
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Agent non trouvé

### GET /api/agents/:id/logs

Récupère les logs d'un agent spécifique.

**Requête:** Query parameters
\`\`\`
?date=2023-06-15&level=error
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "timestamp": "2023-06-15T16:20:45",
      "level": "error",
      "message": "Erreur lors de l'analyse des données : API timeout",
      "details": {
        "errorCode": "API_TIMEOUT",
        "endpoint": "https://api.example.com/data",
        "responseTime": 30000
      }
    },
    {
      "timestamp": "2023-06-15T16:21:30",
      "level": "error",
      "message": "Échec de la reconnexion à l'API",
      "details": {
        "errorCode": "CONNECTION_FAILED",
        "endpoint": "https://api.example.com/data",
        "attempts": 3
      }
    }
  ],
  "total": 2
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Agent non trouvé

## Niches

### GET /api/niches

Récupère la liste des niches.

**Requête:** Query parameters
\`\`\`
?status=profitable
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "id": 1,
      "name": "Immobilier",
      "status": "profitable",
      "campaigns": 2,
      "leads": 440,
      "conversion": 7.8,
      "cpl": 1.85,
      "recommendation": "continue"
    },
    {
      "id": 2,
      "name": "Juridique",
      "status": "profitable",
      "campaigns": 1,
      "leads": 215,
      "conversion": 5.2,
      "cpl": 2.1,
      "recommendation": "continue"
    },
    {
      "id": 3,
      "name": "Architecture",
      "status": "profitable",
      "campaigns": 1,
      "leads": 189,
      "conversion": 9.1,
      "cpl": 1.65,
      "recommendation": "scale"
    }
  ],
  "total": 3
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### GET /api/niches/:id/recommendations

Récupère les recommandations pour une niche spécifique.

**Requête:** Aucun corps de requête, juste l'ID dans l'URL.

**Réponse (200 OK):**
\`\`\`json
{
  "id": 3,
  "name": "Architecture",
  "status": "profitable",
  "recommendation": "scale",
  "analysis": {
    "strengths": [
      "Taux de conversion élevé (9.1%)",
      "Coût par lead faible (1.65€)",
      "Marché en croissance"
    ],
    "opportunities": [
      "Expansion géographique possible",
      "Potentiel de cross-selling avec d'autres services"
    ],
    "actions": [
      "Augmenter le budget de 50%",
      "Élargir la cible géographique",
      "Créer une campagne spécifique pour les architectes d'intérieur"
    ]
  },
  "metrics": {
    "roi": 450,
    "projectedLeads": 300,
    "projectedRevenue": 15000
  },
  "generatedAt": "2023-06-15T12:30:00Z"
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Niche non trouvée

## Statistiques et Analytics

### GET /api/stats/overview

Récupère une vue d'ensemble des statistiques.

**Requête:** Query parameters
\`\`\`
?period=30d
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "leadsCollected": {
    "value": 2543,
    "change": 19,
    "trend": "up"
  },
  "conversionRate": {
    "value": 8.2,
    "change": 2.1,
    "trend": "up"
  },
  "openRate": {
    "value": 24.5,
    "change": 4.3,
    "trend": "up"
  },
  "costPerLead": {
    "value": 2.35,
    "change": -0.45,
    "trend": "down"
  },
  "activeCampaigns": 12,
  "activeAgents": 6,
  "period": {
    "start": "2023-05-15",
    "end": "2023-06-15"
  }
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### GET /api/stats/campaigns

Récupère les statistiques des campagnes.

**Requête:** Query parameters
\`\`\`
?period=30d&campaignId=1,2,3
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "campaigns": [
    {
      "id": 1,
      "name": "Agences immobilières Paris",
      "leads": 342,
      "conversion": 7.8,
      "cpl": 1.85,
      "roi": 420
    },
    {
      "id": 2,
      "name": "Avocats d'affaires Lyon",
      "leads": 215,
      "conversion": 5.2,
      "cpl": 2.1,
      "roi": 310
    },
    {
      "id": 3,
      "name": "Architectes Bordeaux",
      "leads": 189,
      "conversion": 9.1,
      "cpl": 1.65,
      "roi": 550
    }
  ],
  "totals": {
    "leads": 746,
    "averageConversion": 7.4,
    "averageCpl": 1.87,
    "totalCost": 1394.02,
    "estimatedRevenue": 5968.00,
    "roi": 428
  },
  "period": {
    "start": "2023-05-15",
    "end": "2023-06-15"
  }
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

## Utilisateurs et Permissions

### GET /api/users

Récupère la liste des utilisateurs.

**Requête:** Query parameters
\`\`\`
?role=admin&status=active
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "data": [
    {
      "id": "1",
      "name": "Admin",
      "email": "admin@berinia.com",
      "role": "admin",
      "avatar": "A",
      "lastLogin": "10/06/2023 15:45",
      "status": "active",
      "createdAt": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "totalPages": 1
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé (seuls les administrateurs peuvent accéder à cette ressource)

### PUT /api/users/:id/status

Active ou désactive un utilisateur.

**Requête:**
\`\`\`json
{
  "status": "inactive",
  "reason": "Départ de l'entreprise"
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "id": "5",
  "name": "Sophie Lefebvre",
  "status": "inactive",
  "updatedAt": "2023-06-15T17:30:00Z",
  "updatedBy": "1",
  "reason": "Départ de l'entreprise"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Statut invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Utilisateur non trouvé

## Paramètres

### GET /api/settings/general

Récupère les paramètres généraux.

**Requête:** Aucun corps de requête.

**Réponse (200 OK):**
\`\`\`json
{
  "companyName": "BerinIA",
  "adminEmail": "admin@berinia.com",
  "timezone": "Europe/Paris",
  "language": "fr",
  "limits": {
    "maxLeadsPerScrape": 500,
    "maxCampaignsActive": 20,
    "conversionThreshold": 5,
    "cplThreshold": 3
  }
}
\`\`\`

**Erreurs:**
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé

### PUT /api/settings/integrations

Met à jour les paramètres d'intégration.

**Requête:**
\`\`\`json
{
  "slack": {
    "enabled": true,
    "webhookUrl": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
    "channel": "#berinia-alerts"
  },
  "airtable": {
    "enabled": true,
    "apiKey": "key00000000000000",
    "baseId": "app00000000000000",
    "tableName": "Leads"
  },
  "ghl": {
    "enabled": true,
    "apiKey": "ghl_00000000000000000000000000000000",
    "locationId": "loc_00000000000"
  },
  "apify": {
    "enabled": true,
    "apiKey": "apify_api_00000000000000000000000000000000"
  },
  "openai": {
    "enabled": true,
    "apiKey": "sk-00000000000000000000000000000000",
    "model": "gpt-4"
  }
}
\`\`\`

**Réponse (200 OK):**
\`\`\`json
{
  "message": "Paramètres d'intégration mis à jour avec succès",
  "updatedAt": "2023-06-15T18:00:00Z",
  "updatedBy": "1"
}
\`\`\`

**Erreurs:**
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
