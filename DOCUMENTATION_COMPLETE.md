# Documentation Complète du Système infra-ia

## Table des matières

1. [Introduction et vue d'ensemble](#introduction-et-vue-densemble)
2. [Architecture du système](#architecture-du-système)
   - [Structure du projet](#structure-du-projet)
   - [Agents et leur rôle](#agents-et-leur-rôle)
   - [Flux d'information et interactions](#flux-dinformation-et-interactions)
3. [Intégration avec Berinia](#intégration-avec-berinia)
   - [Architecture d'intégration](#architecture-dintégration)
   - [Connecteur de base de données](#connecteur-de-base-de-données)
   - [API REST](#api-rest)
4. [Composants clés](#composants-clés)
   - [Agents de scraping](#agents-de-scraping)
   - [Agents de traitement](#agents-de-traitement)
   - [Agents d'analyse](#agents-danalyse)
   - [Agents de contrôle](#agents-de-contrôle)
   - [Mémoire vectorielle](#mémoire-vectorielle)
5. [Modes de fonctionnement](#modes-de-fonctionnement)
   - [Mode réactif (sur demande)](#mode-réactif-sur-demande)
   - [Mode autonome (planifié)](#mode-autonome-planifié)
6. [Améliorations récentes](#améliorations-récentes)
   - [Persistance des campagnes](#persistance-des-campagnes)
   - [Correction de l'API Berinia](#correction-de-lapi-berinia)
   - [Intégration des agents de débogage](#intégration-des-agents-de-débogage)
7. [Déploiement et configuration](#déploiement-et-configuration)
   - [Prérequis](#prérequis)
   - [Installation](#installation)
   - [Configuration](#configuration)
8. [Tests et validation](#tests-et-validation)
   - [Tests unitaires](#tests-unitaires)
   - [Tests d'intégration](#tests-dintégration)
9. [État actuel et TODO](#état-actuel-et-todo)
   - [Fonctionnalités complétées](#fonctionnalités-complétées)
   - [Tâches en attente](#tâches-en-attente)
10. [Bonnes pratiques et maintenance](#bonnes-pratiques-et-maintenance)
11. [Points d'attention et restrictions](#points-dattention-et-restrictions)

---

## Introduction et vue d'ensemble

infra-ia est un système multi-agents conçu pour automatiser le processus de génération et de gestion de leads pour différentes niches commerciales. Le système s'intègre avec la plateforme Berinia, qui fournit l'interface utilisateur et la gestion de base de données.

BerinIA est une plateforme d'intelligence artificielle autonome qui cible les TPE/PME pour l'installation de solutions d'IA comme des **chatbots IA** pour sites web et des **standards téléphoniques IA**.

L'architecture est composée d'agents intelligents spécialisés qui collaborent pour automatiser l'ensemble du processus de prospection, d'exécution et d'adaptation.

### Principes fondamentaux des agents

Tous les agents suivent les principes clés suivants :
- **Intelligence par prompting GPT-4.1** : Pas de logique en dur ou de seuils arbitraires
- **Rôles uniques et autonomes** : Chaque agent a une responsabilité claire
- **Entraînabilité** : Tous les agents peuvent être améliorés par injection de connaissances
- **Data-driven** : Les décisions sont basées sur des données plutôt que des hypothèses

### Optimisation des modèles LLM

Les agents utilisent une sélection intelligente des modèles GPT-4.1 en fonction de la complexité des tâches :
- **GPT-4.1** : Pour les tâches complexes nécessitant une réflexion avancée
- **GPT-4.1 Mini** : Pour les tâches de complexité moyenne
- **GPT-4.1 Nano** : Pour les tâches simples et fréquentes

---

## Architecture du système

### Structure du projet

```
infra-ia/
├── agents/                   # Agents spécialisés pour différentes tâches
│   ├── analytics/            # Analyse de campagnes et performances
│   ├── base/                 # Classes de base pour tous les agents
│   ├── classifier/           # Classification des leads
│   ├── cleaner/              # Nettoyage et validation des leads
│   ├── controller/           # Coordination et orchestration des flux
│   ├── exporter/             # Export des leads vers le CRM/DB
│   ├── knowledge/            # Gestion des connaissances et enrichissement
│   ├── logs/                 # Journalisation des activités
│   ├── messenger/            # Envoi de messages aux leads
│   ├── pivot/                # Prise de décision sur les leads
│   ├── scraper/              # Collecte de leads depuis diverses sources
│   └── utils/                # Utilitaires pour les agents
├── config/                   # Configuration du système
├── db/                       # Connecteurs pour base de données locale
├── integrations/             # Modules d'intégration avec services externes
│   └── berinia/              # Intégration avec le backend Berinia
├── logs/                     # Journaux d'exécution
├── memory/                   # Gestion de la mémoire vectorielle
├── prompts/                  # Templates de prompts pour les agents LLM
├── scripts/                  # Scripts utilitaires
│   ├── deployment/           # Scripts de déploiement
│   └── migration/            # Scripts de migration
├── templates/                # Templates pour la génération de contenu
├── tests/                    # Tests et validation du système
└── utils/                    # Utilitaires système généraux
```

### Agents et leur rôle

#### Agents stratégiques

1. **StrategyAgent**
   - **Rôle** : Choisir intelligemment une nouvelle niche à cibler
   - **Comportement** : Analyse les données des campagnes passées et recommande une niche non testée avec justification
   - **Intégration** : Évite les niches déjà testées par accès à la base de données des campagnes

2. **PlanningAgent**
   - **Rôle** : Décider si une campagne peut être lancée aujourd'hui
   - **Comportement** : Analyse la charge système, les ressources disponibles et priorise les lancements
   - **Intégration** : Suit les campagnes en cours et la planification

3. **MemoryManagerAgent**
   - **Rôle** : Gérer la mémoire vectorielle Qdrant
   - **Comportement** : Vérifie la cohérence, nettoie les doublons, interroge la base de connaissances
   - **Intégration** : Interface avec Qdrant pour toutes les opérations vectorielles

#### Agents d'exécution

4. **CampaignStarterAgent**
   - **Rôle** : Orchestrer le démarrage et l'exécution d'une campagne
   - **Comportement** : Coordonne les étapes de scraping, nettoyage, classification, export et contact
   - **Intégration** : Pilote les agents spécialisés dans une séquence efficace
   - **Nouveauté** : Intègre désormais multiple sources de scraping (Apify et Apollo)

5. **ApifyScraper**
   - **Rôle** : Extraire des leads depuis diverses sources web avec Apify
   - **Comportement** : Scrape les informations de contact des entreprises dans une niche cible
   - **Intégration** : Connecté à la plateforme Apify pour des données larges mais génériques

6. **ApolloScraper**
   - **Rôle** : Extraire des leads B2B qualifiés via Apollo.io
   - **Comportement** : Utilise des filtres précis pour extraire des contacts décisionnaires
   - **Intégration** : Source de données complémentaire avec filtres avancés (titre, taille d'entreprise, signaux d'achat)

7. **CleanerAgent**
   - **Rôle** : Nettoyer les données de leads avant utilisation
   - **Comportement** : Détecte et corrige les erreurs de format, enrichit les données manquantes
   - **Intégration** : Prépare les données pour la classification et l'export

8. **LeadClassifierAgent**
   - **Rôle** : Classifier la qualité des leads
   - **Comportement** : Catégorise les leads en "chaud", "tiède" ou "froid" selon critères
   - **Intégration** : Priorise les leads pour les actions de contact

9. **CRMExporterAgent**
   - **Rôle** : Gérer l'export stratégique des leads vers le CRM
   - **Comportement** : Décide quels leads exporter immédiatement ou mettre en attente
   - **Intégration** : Interface avec le CRM pour l'envoi de leads qualifiés

10. **MessengerAgent**
    - **Rôle** : Gérer les communications multi-canal avec les leads
    - **Comportement** : Choisit le canal optimal (email/SMS), le moment et personnalise les messages
    - **Intégration** : Remplace et coordonne les anciens EmailSender et SMSSender

#### Agents d'analyse

11. **AnalyticsAgent**
    - **Rôle** : Analyser les performances des campagnes passées
    - **Comportement** : Examine les données pour identifier les patterns de succès/échec
    - **Intégration** : Utilise PostgreSQL pour accéder aux données de campagne

12. **PivotAgent**
    - **Rôle** : Décider de pivoter, continuer ou dupliquer une campagne
    - **Comportement** : Prend une décision stratégique basée sur les résultats de l'AnalyticsAgent
    - **Intégration** : Utilise les analyses pour orienter les futures campagnes

13. **AgentLoggerAgent**
    - **Rôle** : Surveiller et analyser les décisions des autres agents
    - **Comportement** : Enregistre les prises de décision et en extrait des insights
    - **Intégration** : Archive les logs pour amélioration continue

#### Agent de connaissance

14. **KnowledgeInjectorAgent**
    - **Rôle** : Injecter des connaissances dans la mémoire vectorielle
    - **Comportement** : Extrait des connaissances depuis forums, vidéos, Reddit, etc.
    - **Intégration** : Coordonne l'extraction via RedditScraper et YouTubeScraper puis injecte dans Qdrant
    - **Objectif** : Améliorer continuellement les autres agents avec des connaissances à jour

### Flux d'information et interactions

```
StrategyAgent → PlanningAgent → CampaignStarterAgent → [Scraping/Cleaning/Classification] → CRMExporter → MessengerAgent
                                                                  ↑
       AnalyticsAgent → PivotAgent                               |
                 ↑                                               |
                 |                                               |
         [Base de données]                                       |
                 ↑                                               |
    MemoryManagerAgent ← KnowledgeInjectorAgent — — — — — — — — —+
```

Le système fonctionne selon un pipeline séquentiel:

1. **Collecte de leads** (Scraper) depuis différentes sources web
2. **Nettoyage et validation** (Cleaner) pour garantir la qualité des données
3. **Classification** (Classifier) pour prioriser les leads les plus prometteurs
4. **Enrichissement** (Knowledge) avec des données contextuelles
5. **Prise de décision** (Pivot) pour déterminer les actions à prendre
6. **Communication** (Messenger) pour contacter les prospects
7. **Exportation** (CRM Exporter) vers la base de données Berinia
8. **Analyse** (Analytics) pour évaluer les performances

---

## Intégration avec Berinia

### Architecture d'intégration

L'architecture est composée de plusieurs couches :

1. **Service d'agents** : Un serveur FastAPI qui expose les agents via une API REST
2. **Adaptateur Berinia** : Module qui permet à Berinia de communiquer avec le service d'agents
3. **Backend Berinia** : Le système de gestion SaaS qui stocke les données dans PostgreSQL
4. **Frontend Berinia** : L'interface utilisateur existante qui interagit avec les agents

### Connecteur de base de données

Un module d'intégration directe entre le système infra-ia et la base de données PostgreSQL de Berinia a été développé. Cette intégration permet au CRMExporterAgent d'exporter directement les leads dans la base de données.

Le module principal d'intégration (`db_connector.py`) :
- Établit une connexion sécurisée à la base de données PostgreSQL
- Mappe les leads du format infra-ia vers Berinia
- Gère les transactions et les erreurs

```python
# Exemple d'utilisation
from integrations.berinia.db_connector import export_leads_to_berinia

# Exporter des leads vers Berinia
result = export_leads_to_berinia(leads, campaign_id=1)
```

#### Points importants pour l'intégration avec la base de données

1. **Contrainte de clé étrangère**: Chaque lead doit être associé à une campagne existante (via `campagne_id`).
2. **Structure des leads**: Les leads doivent contenir au moins un nom et une adresse email valide.
3. **Gestion des erreurs**: Le module gère les erreurs d'insertion et tente de poursuivre avec les autres leads.
4. **Compatibilité des formats**: Les champs des leads doivent être correctement mappés entre infra-ia et Berinia:
   - `company_name` -> `entreprise`
   - `contact_name` -> `nom`
   - `email` -> `email`
   - `phone` -> `telephone`

### API REST

Le système s'intègre avec la plateforme Berinia via une API REST (api_service.py) qui expose les fonctionnalités des agents. Le service est configuré dans `api_service.py` et peut être déployé comme service système via `infra-ia-agents.service`.

```bash
# Démarrer le service API
sudo systemctl start infra-ia-agents
```

---

## Composants clés

### Agents de scraping

#### ApifyScraper

Responsable de la collecte de leads à partir de diverses sources en ligne, principalement via l'API Apify. L'agent nettoie les données brutes et les normalise en un format standard.

```python
# Utilisation de l'agent scraper
from agents.scraper.apify_client_scraper import ApifyClientScraper

scraper = ApifyClientScraper()
results = scraper.run({
    "niche": "restaurants",
    "location": "Paris, France",
    "max_results": 50
})
```

#### ApolloScraper

Extrait des leads B2B qualifiés via Apollo.io en utilisant des filtres précis pour extraire des contacts décisionnaires.

### Agents de traitement

#### LeadCleaner

Responsable du nettoyage et de la validation des leads. L'agent vérifie les données et s'assure qu'elles sont complètes et valides.

#### LeadClassifierAgent

Analyse les leads et leur attribue un score de qualité, permettant ainsi de prioriser les leads les plus prometteurs.

#### MessengerAgent

Gère la communication avec les leads, en utilisant des templates personnalisés pour les emails et SMS.

#### CRMExporterAgent

Exporte les leads qualifiés vers la base de données Berinia. C'est le point de jonction entre infra-ia et Berinia.

### Agents d'analyse

#### AnalyticsAgent

Analyse les performances des campagnes passées et identifie les patterns de succès et d'échec.

#### PivotAgent

Décide de pivoter, continuer ou dupliquer une campagne en fonction des résultats d'analyse.

### Agents de contrôle

#### CampaignStarterAgent

Orchestrateur principal qui coordonne le démarrage et l'exécution d'une campagne complète.

#### DecisionBrainAgent

Chef d'orchestre du système qui peut désormais utiliser un ensemble d'agents de débogage intelligents pour diagnostiquer et résoudre automatiquement des problèmes dans l'infrastructure.

### Mémoire vectorielle

Le système utilise Qdrant comme base de données vectorielle pour stocker et récupérer efficacement des connaissances structurées sous forme d'embeddings. Cette mémoire vectorielle est gérée par le MemoryManagerAgent et enrichie par le KnowledgeInjectorAgent.

---

## Modes de fonctionnement

### Mode réactif (sur demande)

Les agents sont déclenchés par les utilisateurs via l'interface Berinia :
- L'utilisateur demande l'exécution d'un agent spécifique
- Le backend Berinia transmet la demande au service d'agents
- L'agent s'exécute et retourne le résultat

### Mode autonome (planifié)

Les agents s'exécutent automatiquement selon une planification configurée :
- Le service d'agents maintient un calendrier d'exécution
- Les agents sont exécutés automatiquement aux moments prévus
- Les résultats sont enregistrés et consultables via l'API

---

## Améliorations récentes

### Persistance des campagnes

Un système de persistance des campagnes a été implémenté pour résoudre le problème des campagnes qui n'étaient pas sauvegardées dans la base de données après leur exécution.

Le module `db/campaign_storage.py` fournit :
- Stockage des campagnes dans un fichier JSON (`db/campaigns.json`)
- Fonctions pour sauvegarder, récupérer et filtrer les campagnes
- Support pour les campagnes actives et complétées

Avantages :
- **Simple et robuste** : Utilisation d'un fichier JSON pour le stockage
- **Facilement extensible** : Structure modulaire pour ajout de fonctionnalités
- **Compatible** : Fonctionne avec les interfaces existantes
- **Traçabilité** : Chaque campagne est correctement enregistrée avec ses métadonnées

### Correction de l'API Berinia

Des corrections ont été apportées à l'API Berinia pour résoudre plusieurs problèmes :

1. **Problèmes d'indentation** : Correction de l'indentation dans les fichiers d'endpoints
2. **Erreur "dict object has no attribute '_sa_instance_state'"** : Utilisation de `jsonable_encoder` pour sérialiser les objets SQLAlchemy
3. **Erreur "dict object is not callable"** : Correction des appels multiples ou imbriqués à `jsonable_encoder`
4. **Erreur "router is not defined"** : Décommentage des lignes définissant le router
5. **Erreur 404 Not Found pour les endpoints** : Suppression des préfixes dupliqués dans les définitions de router

Le service Berinia API est maintenant opérationnel et les endpoints principaux fonctionnent correctement:
- /api/campaigns/
- /api/niches/

### Intégration des agents de débogage

Le Decision Brain Agent peut maintenant utiliser un ensemble d'agents de débogage intelligents pour diagnostiquer et résoudre automatiquement des problèmes dans l'infrastructure.

Agents de débogage disponibles :

1. **SmartDebugger** : Agent avec mémoire vectorielle pour identifier et corriger les problèmes courants
2. **FastAPIDiagnostic** : Agent spécialisé pour les applications FastAPI
3. **BeriniaIntelligentFixer** : Agent spécifique à la plateforme Berinia

Avantages pour le Decision Brain Agent :
- **Autonomie accrue** : Résolution automatique de nombreux problèmes
- **Mémoire partagée** : Expériences de débogage intégrées à la mémoire globale
- **Proactivité** : Surveillance régulière pour détecter les problèmes en amont
- **Apprentissage continu** : Amélioration continue avec chaque problème rencontré

---

## Déploiement et configuration

### Prérequis

- Python 3.10+
- PostgreSQL
- Serveur avec 4+ Go de RAM

### Installation

1. Déployer le service d'agents :
   ```bash
   # Cloner le repo
   git clone https://github.com/berinia/infra-ia.git
   cd infra-ia
   
   # Installer les dépendances
   pip install -r requirements.txt
   
   # Configurer
   cp config/.env.example config/.env
   # Éditer le fichier .env avec vos clés API et paramètres
   
   # Démarrer le service
   python api_service.py
   ```

2. Configurer le connecteur Berinia :
   ```bash
   # Éditer les paramètres de connexion dans
   vim integrations/berinia/db_connector.py
   ```

### Configuration

Les principaux fichiers de configuration sont :

- `config/.env` : Variables d'environnement et clés API
- `config/scoring_config.json` : Configuration des scores pour la classification des leads
- `config/business_heuristics.json` : Règles métier pour les décisions des agents
- `config/debugging_config.json` : Configuration des agents de débogage

---

## Tests et validation

### Tests unitaires

Des tests unitaires sont disponibles pour chaque agent dans le répertoire `tests/`.

### Tests d'intégration

Des tests d'intégration pour valider le fonctionnement de bout en bout du système :

```bash
# Tester l'intégration avec la base de données
python3 /root/infra-ia/tests/scripts/insert_test_leads_updated.py

# Exécuter le test système complet
python3 /root/infra-ia/tests/test_full_system.py --niche "restaurant" --location "Paris, France" --max-leads 10
```

---

## État actuel et TODO

### Fonctionnalités complétées

- ✅ Architecture de base des agents multiples
- ✅ Intégration avec Berinia pour l'export de leads
- ✅ Système de persistance des campagnes
- ✅ Correction de l'API Berinia
- ✅ Intégration des agents de débogage

### Tâches en attente

Restent à accomplir selon le TODO.md :

1. **Agents de scraping** :
   - [ ] Configurer les clés API réelles (Apify, Apollo)
   - [ ] Implémenter les limites de requêtes API
   - [ ] Tester avec des données réelles
   - [ ] Améliorer le stockage des résultats

2. **Mémoire vectorielle** :
   - [ ] Vérifier l'installation de Qdrant
   - [ ] Implémenter des embeddings réels
   - [ ] Optimiser l'intégration aux agents de connaissance
   - [ ] Effectuer des tests de performance

3. **Agents de connaissance** :
   - [ ] Compléter le KnowledgeInjectorAgent
   - [ ] Implémenter correctement le VectorInjector
   - [ ] Ajouter et tester les sources de connaissance

4. **Sécurité et API** :
   - [ ] Implémenter l'authentification pour l'API
   - [ ] Ajouter des contrôles d'accès
   - [ ] Documenter les formats d'entrée/sortie

5. **Déploiement** :
   - [ ] Finaliser la conteneurisation Docker
   - [ ] Configurer le service systemd
   - [ ] Optimiser pour la mise à l'échelle

---

## Bonnes pratiques et maintenance

1. **Suivre l'architecture existante** : Respecter la séparation des responsabilités entre les agents.

2. **Tester régulièrement l'intégration** : Vérifier que les leads sont correctement exportés vers Berinia.

3. **Journaliser les actions** : Toutes les actions importantes doivent être journalisées pour le debugging.

4. **Gérer les erreurs gracieusement** : Prendre en compte les erreurs potentielles et implémenter des mécanismes de fallback.

5. **Documenter les changements** : Documenter toute modification apportée au système pour faciliter la maintenance future.

Pour maintenir l'API en bon état de fonctionnement :

1. Toujours utiliser `jsonable_encoder` pour sérialiser les objets SQLAlchemy
2. Ne pas ajouter de préfixes dans les définitions de router des fichiers d'endpoints
3. Éviter les manipulations directes des attributs d'objets SQLAlchemy
4. Maintenir une indentation cohérente dans le code Python

---

## Points d'attention et restrictions

1. **Dépendance à PostgreSQL** : La base de données Berinia fonctionne avec PostgreSQL. Les modèles de données et contraintes doivent être respectés.

2. **Authentification** : Les identifiants de connexion à la base de données sont définis dans le fichier `.env` du backend Berinia.

3. **Validation des données** : Le système possède plusieurs couches de validation pour garantir l'intégrité des données.

4. **Contrainte de clé étrangère pour les leads** : Tout lead doit être associé à une campagne existante.

5. **Limites des API externes** : Les services comme Apify et Apollo ont des limites de requêtes qu'il faut respecter.
