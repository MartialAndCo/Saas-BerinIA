# Liste des vérifications nécessaires pour l'infrastructure d'agents IA

Cette liste détaille les points qui doivent être vérifiés et les actions requises avant de considérer l'infrastructure comme prête à être intégrée avec Berinia.

## 1. Agents de scraping

- [ ] **Configurer les clés API réelles**
  - [ ] Créer un compte et obtenir une clé API Apify
  - [ ] Créer un compte et obtenir une clé API Apollo
  - [ ] Sécuriser le stockage des clés (environnement ou coffre-fort)

- [ ] **Implémenter les limites de requêtes API**
  - [ ] Vérifier les limites quotidiennes/mensuelles des API
  - [ ] Implémenter un système de file d'attente pour respecter les limites de taux
  - [ ] Ajouter la gestion des erreurs et des retries en cas d'échec

- [ ] **Tester avec des données réelles**
  - [ ] Faire des appels d'API réels avec des niches spécifiques
  - [ ] Vérifier le nettoyage des données entrantes
  - [ ] Valider le déduplication des leads

- [ ] **Stockage des résultats**
  - [ ] Implémenter la persistance des résultats de scraping
  - [ ] Configurer la DB pour stocker l'historique des recherches

## 2. Mémoire vectorielle

- [ ] **Vérifier l'installation de Qdrant**
  - [ ] Confirmer que Qdrant est correctement installé et fonctionne
  - [ ] Tester la création/suppression de collections

- [ ] **Implémenter des embeddings réels**
  - [ ] Configurer une clé API OpenAI pour les embeddings
  - [ ] Ajouter une alternative locale pour les embeddings (si nécessaire)

- [ ] **Intégration aux agents de connaissance**
  - [ ] Vérifier que les agents utilisent correctement VectorStore
  - [ ] Tester la récupération similaire avec des requêtes réelles

- [ ] **Tests de performance**
  - [ ] Mesurer les temps de réponse pour les requêtes vectorielles
  - [ ] Vérifier la scalabilité avec un grand nombre de vecteurs

## 3. Agents de connaissance

- [ ] **Compléter les agents inachevés**
  - [ ] Terminer le KnowledgeInjectorAgent
  - [ ] Implémenter correctement le VectorInjector

- [ ] **Tests des sources de connaissance**
  - [ ] Vérifier le scraping Reddit
  - [ ] Vérifier le scraping YouTube
  - [ ] Ajouter d'autres sources pertinentes

- [ ] **Intégration avec LLM**
  - [ ] Tester la génération de contenu à partir des connaissances
  - [ ] Vérifier l'utilisation correcte des connaissances dans les prompts

## 4. Tests complets des agents

- [ ] **Tests unitaires**
  - [ ] Créer des tests pour chaque agent individuellement
  - [ ] Tests mock pour isoler les dépendances

- [ ] **Tests d'intégration**
  - [ ] Tester la chaîne complète : scraping -> cleaning -> classification -> messaging
  - [ ] Vérifier les interactions entre agents

- [ ] **Tests de récupération d'erreur**
  - [ ] Simuler des échecs et vérifier la récupération
  - [ ] Tester les timeouts et les retries

## 5. API et communication

- [ ] **Sécurité de l'API**
  - [ ] Implémenter l'authentification pour l'API
  - [ ] Ajouter des contrôles d'accès
  - [ ] Protéger les points d'extrémité sensibles

- [ ] **Documentation**
  - [ ] Documenter les formats d'entrée/sortie de chaque endpoint
  - [ ] Ajouter des exemples de requêtes

- [ ] **Monitoring et logs**
  - [ ] Implémenter un système de monitoring des performances
  - [ ] Centraliser les logs pour une meilleure visibilité

## 6. Déploiement et infrastructure

- [ ] **Conteneurisation**
  - [ ] Créer des Dockerfiles pour chaque composant
  - [ ] Configurer docker-compose pour le développement

- [ ] **Configuration Systemd**
  - [ ] Finaliser le service systemd
  - [ ] Ajouter des scripts de démarrage/arrêt

- [ ] **Mise à l'échelle**
  - [ ] Évaluer les besoins de mise à l'échelle
  - [ ] Déterminer les goulets d'étranglement potentiels

## 7. Intégration Berinia

- [ ] **Tests d'intégration bidirectionnelle**
  - [ ] Vérifier les appels de Berinia vers les agents
  - [ ] Vérifier les appels des agents vers Berinia

- [ ] **Synchronisation des données**
  - [ ] Implémenter un système de synchronisation des leads/campagnes
  - [ ] Gérer les mises à jour bidirectionnelles

- [ ] **Gestion des utilisateurs**
  - [ ] Synchroniser les permissions utilisateur
  - [ ] Respecter les limites par utilisateur/compte

## Actions prioritaires

1. Obtenir les clés API réelles pour les services de scraping et d'embedding
2. Vérifier l'installation et le fonctionnement de Qdrant
3. Tester chaque agent individuellement avec des données réelles
4. Implémenter l'authentification pour l'API
5. Faire des tests d'intégration complète de bout en bout
