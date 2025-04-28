# Architecture BerinIA - Vue d'ensemble

## Introduction

BerinIA est une plateforme d'intelligence artificielle autonome qui cible les TPE/PME pour l'installation de solutions d'IA :
- **Chatbots IA** pour sites web (réponse aux clients, explication des services, redirection)
- **Standards téléphoniques IA** (prise d'appels, qualification des demandes, redirection, prise de RDV)

L'architecture est composée d'agents intelligents spécialisés qui collaborent pour automatiser l'ensemble du processus de prospection, d'exécution et d'adaptation.

## Principes fondamentaux des agents

Tous nos agents suivent les principes clés suivants :
- **Intelligence par prompting GPT-4.1** : Pas de logique en dur ou de seuils arbitraires
- **Rôles uniques et autonomes** : Chaque agent a une responsabilité claire
- **Entraînabilité** : Tous les agents peuvent être améliorés par injection de connaissances
- **Data-driven** : Les décisions sont basées sur des données plutôt que des hypothèses

## Agents clés et leur rôle

### Agents stratégiques

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

### Agents d'exécution

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

### Agents d'analyse

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

### Agent de connaissance

14. **KnowledgeInjectorAgent**
    - **Rôle** : Injecter des connaissances dans la mémoire vectorielle
    - **Comportement** : Extrait des connaissances depuis forums, vidéos, Reddit, etc.
    - **Intégration** : Coordonne l'extraction via RedditScraper et YouTubeScraper puis injecte dans Qdrant
    - **Objectif** : Améliorer continuellement les autres agents avec des connaissances à jour

## Flux d'information et interactions

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

## Infrastructure technique

1. **Base de données** : PostgreSQL pour stockage relationnel des campagnes/leads
2. **Mémoire vectorielle** : Qdrant pour stockage de connaissances sous forme vectorielle
3. **Modèle LLM** : GPT-4.1 pour le raisonnement des agents
4. **Orchestration** : Système basé sur langgraph pour coordonner les agents
5. **Logging** : Système centralisé pour traçabilité et amélioration continue

## Points forts de l'architecture

1. **Modularité** : Chaque agent a une responsabilité unique et bien définie
2. **Adaptabilité** : Le système apprend et s'améliore sur la base des résultats
3. **Scalabilité** : L'architecture permet d'ajouter de nouveaux agents ou de raffiner les existants
4. **Autonomie** : L'ensemble du système peut fonctionner sans intervention humaine
5. **Intelligence collective** : Les agents collaborent pour optimiser les résultats globaux

## Évolution et Maintenance

L'architecture est conçue pour évoluer :
- Les agents peuvent être améliorés individuellement grâce à l'injection de connaissances
- De nouveaux agents peuvent être ajoutés pour des besoins spécifiques
- Les prompts des agents sont stockés dans des fichiers dédiés pour faciliter les mises à jour
