# Documentation du système infra-ia

## Vue d'ensemble

infra-ia est un système multi-agents conçu pour automatiser le processus de génération et de gestion de leads pour différentes niches commerciales. Le système s'intègre avec la plateforme Berinia, qui fournit l'interface utilisateur et la gestion de base de données.

## Architecture du système

### Structure principale

Le projet est structuré en plusieurs composants clés:

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
│   ├── data/                 # Données de test
│   ├── scripts/              # Scripts de test spécifiques
└── utils/                    # Utilitaires système généraux
```

### Flux de travail principal

Le système fonctionne selon un pipeline séquentiel:

1. **Collecte de leads** (Scraper) depuis différentes sources web
2. **Nettoyage et validation** (Cleaner) pour garantir la qualité des données
3. **Classification** (Classifier) pour prioriser les leads les plus prometteurs
4. **Enrichissement** (Knowledge) avec des données contextuelles
5. **Prise de décision** (Pivot) pour déterminer les actions à prendre
6. **Communication** (Messenger) pour contacter les prospects
7. **Exportation** (CRM Exporter) vers la base de données Berinia
8. **Analyse** (Analytics) pour évaluer les performances

## Agents principaux

### ApifyScraper

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

### LeadCleaner

Responsable du nettoyage et de la validation des leads. L'agent vérifie les données et s'assure qu'elles sont complètes et valides.

### LeadClassifierAgent

Analyse les leads et leur attribue un score de qualité, permettant ainsi de prioriser les leads les plus prometteurs.

### MessengerAgent

Gère la communication avec les leads, en utilisant des templates personnalisés pour les emails et SMS.

### CRMExporterAgent

Exporte les leads qualifiés vers la base de données Berinia. C'est le point de jonction entre infra-ia et Berinia.

## Intégration avec Berinia

Le système infra-ia s'intègre avec la plateforme Berinia de deux manières:

### 1. Via l'API REST (api_service.py)

L'API permet d'exposer les fonctionnalités des agents à Berinia via des endpoints HTTP. Le service est configuré dans `api_service.py` et peut être déployé comme service système via `infra-ia-agents.service`.

```bash
# Démarrer le service API
sudo systemctl start infra-ia-agents
```

### 2. Via la connexion directe à la base de données (integrations/berinia/db_connector.py)

Une intégration directe a été mise en place pour permettre aux agents d'exporter les leads directement dans la base de données PostgreSQL de Berinia.

Ce connecteur établit une connexion sécurisée à la base de données, mappe les leads du format infra-ia vers le format attendu par Berinia, et gère les erreurs et transactions.

```python
# Exemple d'utilisation du connecteur DB
from integrations.berinia.db_connector import export_leads_to_berinia

# Les leads doivent être associés à une campagne existante
leads = [...]  # Liste de leads à exporter
campaign_id = 1  # ID de la campagne dans Berinia

result = export_leads_to_berinia(leads, campaign_id)
```

#### Points importants pour l'intégration avec la base de données

1. **Contrainte de clé étrangère**: Chaque lead doit être associé à une campagne existante (via `campagne_id`).
2. **Structure des leads**: Les leads doivent contenir au moins un nom et une adresse email valide.
3. **Gestion des erreurs**: Le module gère les erreurs d'insertion et tente de poursuivre avec les autres leads.

Pour créer une campagne de test pour vos développements, vous pouvez utiliser le script:
```bash
python3 /root/infra-ia/tests/scripts/create_test_campaign_direct.py
```

## Points d'attention et restrictions

1. **Dépendance à PostgreSQL**: La base de données Berinia fonctionne avec PostgreSQL. Les modèles de données et contraintes doivent être respectés.

2. **Authentification**: Les identifiants de connexion à la base de données sont définis dans le fichier `.env` du backend Berinia.

3. **Validation des données**: Le système possède plusieurs couches de validation pour garantir l'intégrité des données.

4. **Compatibilité des formats**: Les champs des leads doivent être correctement mappés entre infra-ia et Berinia:
   - `company_name` -> `entreprise`
   - `contact_name` -> `nom`
   - `email` -> `email`
   - `phone` -> `telephone`

## Tests et validation

Des scripts de test ont été développés pour valider les différentes parties du système:

```bash
# Tester l'intégration avec la base de données
python3 /root/infra-ia/tests/scripts/insert_test_leads_updated.py

# Exécuter le test système complet
python3 /root/infra-ia/tests/test_full_system.py --niche "restaurant" --location "Paris, France" --max-leads 10
```

## Bonnes pratiques pour les développements futurs

1. **Suivre l'architecture existante**: Respecter la séparation des responsabilités entre les agents.

2. **Tester régulièrement l'intégration**: Vérifier que les leads sont correctement exportés vers Berinia.

3. **Journaliser les actions**: Toutes les actions importantes doivent être journalisées pour le debugging.

4. **Gérer les erreurs gracieusement**: Prendre en compte les erreurs potentielles et implémenter des mécanismes de fallback.

5. **Documenter les changements**: Documenter toute modification apportée au système pour faciliter la maintenance future.

## Résumé des améliorations récentes

1. **Intégration complète avec Berinia**: Les leads sont maintenant correctement exportés et stockés dans la base de données Berinia.

2. **Optimisation du flux de travail**: Le pipeline de traitement des leads a été optimisé pour une meilleure efficacité.

3. **Organisation du projet**: Les fichiers ont été organisés dans une structure cohérente pour faciliter la navigation et la maintenance.

4. **Documentation détaillée**: La documentation a été améliorée pour faciliter la prise en main du système.
