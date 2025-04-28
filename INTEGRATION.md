# Guide d'intégration infra-ia avec Berinia SaaS

Ce document explique comment intégrer les agents IA développés dans `infra-ia` avec la plateforme SaaS `Berinia`.

## Architecture

L'intégration utilise une architecture en microservices :

1. **Service d'agents infra-ia** : API REST exposant les agents via FastAPI (port 8555)
2. **Backend Berinia** : Application FastAPI existante utilisant un adaptateur pour communiquer avec le service d'agents
3. **Frontend Berinia** : Interface utilisateur existante interagissant avec le backend

## Déploiement

### 1. Installation du service d'agents

Sur le serveur de production :

```bash
# Copier les fichiers d'intégration
cd /root/infra-ia
chmod +x start_agent_service.sh

# Installation du service systemd
sudo cp infra-ia-agents.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable infra-ia-agents
sudo systemctl start infra-ia-agents

# Vérifier que le service est en cours d'exécution
sudo systemctl status infra-ia-agents
```

### 2. Configuration de Berinia

Assurez-vous que le backend Berinia peut communiquer avec le service d'agents :

```bash
# Variables d'environnement pour le backend Berinia
export AGENTS_SERVICE_URL="http://localhost:8555"
export AGENTS_REQUEST_TIMEOUT="120"
```

Ces variables doivent être définies dans l'environnement où s'exécute le backend Berinia.

### 3. Configuration Nginx (optionnel)

Pour sécuriser l'accès à l'API des agents via Nginx :

```nginx
# Extrait de la configuration Nginx pour app.berinia.com
location /api/agent-service/ {
    proxy_pass http://localhost:8555/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Test de l'intégration

1. **Vérifier le service d'agents** :
```bash
curl http://localhost:8555/
# Doit renvoyer : {"status":"running","service":"infra-ia agents API"}

curl http://localhost:8555/agents/types
# Doit renvoyer la liste des types d'agents disponibles
```

2. **Tester l'exécution via Berinia** :
```bash
# Exemple de requête pour exécuter un agent analytics
curl -X POST "http://localhost:8000/agents/1/execute" \
     -H "Content-Type: application/json" \
     -d '{"operation":"analyze_campaign","campaign_id":"CAMP001"}'
```

3. **Interface web** :
   - Accédez à `http://app.berinia.com/admin/agents`
   - Sélectionnez un agent et cliquez sur "Exécuter"
   - Vérifiez les logs de l'agent pour confirmer l'exécution

## Dépannage

Si vous rencontrez des problèmes :

1. **Vérifier les logs du service d'agents** :
```bash
sudo journalctl -u infra-ia-agents -f
```

2. **Vérifier les logs de Berinia** :
```bash
# Selon la configuration de logging de Berinia
```

3. **Tester l'API directement** :
```bash
curl -X POST "http://localhost:8555/agents/analytics/execute" \
     -H "Content-Type: application/json" \
     -d '{"operation":"analyze_campaign","campaign_id":"CAMP001"}'
```

## Maintenance

- Pour mettre à jour les agents : modifiez le code dans `infra-ia` et redémarrez le service
```bash
sudo systemctl restart infra-ia-agents
```

- Pour ajouter un nouveau type d'agent : mettez à jour le dictionnaire `AGENT_MAPPING` dans `api_service.py`
