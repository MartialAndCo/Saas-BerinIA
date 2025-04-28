# Architecture d'Intégration Berinia + infra-ia

Ce projet contient l'infrastructure nécessaire pour intégrer les agents IA (infra-ia) avec la plateforme SaaS Berinia.

## Vue d'ensemble

L'architecture est composée de plusieurs couches :

1. **Service d'agents** : Un serveur FastAPI qui expose les agents via une API REST
2. **Adaptateur Berinia** : Module qui permet à Berinia de communiquer avec le service d'agents
3. **Backend Berinia** : Le système de gestion SaaS qui stocke les données dans PostgreSQL
4. **Frontend Berinia** : L'interface utilisateur existante qui interagit avec les agents

## Modes de fonctionnement des agents

Les agents fonctionnent selon deux modes :

### 1. Mode réactif (sur demande)

Les agents sont déclenchés par les utilisateurs via l'interface Berinia :
- L'utilisateur demande l'exécution d'un agent spécifique
- Le backend Berinia transmet la demande au service d'agents
- L'agent s'exécute et retourne le résultat

### 2. Mode autonome (planifié)

Les agents s'exécutent automatiquement selon une planification configurée :
- Le service d'agents maintient un calendrier d'exécution
- Les agents sont exécutés automatiquement aux moments prévus
- Les résultats sont enregistrés et consultables via l'API

## Optimisation des modèles LLM

Les agents utilisent une sélection intelligente des modèles GPT-4.1 :

- **GPT-4.1** : Pour les tâches complexes nécessitant une réflexion avancée
- **GPT-4.1 Mini** : Pour les tâches de complexité moyenne
- **GPT-4.1 Nano** : Pour les tâches simples et fréquentes

## Déploiement

### Prérequis

- Python 3.10+
- PostgreSQL
- Serveur avec 4+ Go de RAM

### Installation

1. Déployer le service d'agents :

```bash
cd /root/infra-ia
./deploy.sh
```

2. Vérifier que le service est en cours d'exécution :

```bash
curl http://localhost:8555/
# Devrait retourner : {"status":"running","service":"infra-ia agents API"}
```

3. Tester l'exécution d'un agent via l'API Berinia :

```bash
curl -X POST http://localhost:8000/api/agents/1/execute \
     -H "Content-Type: application/json" \
     -d '{"operation": "test_operation"}'
```

### Configuration systemd

Pour que le service d'agents démarre automatiquement avec le système, utilisez le fichier service systemd :

```bash
sudo cp /root/infra-ia/infra-ia-agents.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable infra-ia-agents
sudo systemctl start infra-ia-agents
```

## Gestion des agents autonomes

Pour gérer les agents autonomes via l'API :

```bash
# Lister les agents autonomes
curl http://localhost:8555/autonomous-agents

# Configurer un agent autonome
curl -X POST http://localhost:8555/autonomous-agents/analytics/configure \
     -H "Content-Type: application/json" \
     -d '{"agent_type":"analytics","schedule":"daily","input_data":{"operation":"daily_analysis"},"active":true}'

# Activer/désactiver un agent autonome
curl -X POST http://localhost:8555/autonomous-agents/analytics/toggle
```

## Surveillance et logs

Pour surveiller l'exécution des agents :

```bash
# Lister les jobs récents
curl http://localhost:8555/jobs

# Voir les détails d'un job spécifique
curl http://localhost:8555/jobs/analytics_1714151225
```

Pour les logs système :

```bash
sudo journalctl -u infra-ia-agents -f
