#!/bin/bash

# Script de démarrage du service d'agents infra-ia

# Variables d'environnement
export AGENTS_API_PORT=${AGENTS_API_PORT:-8555}
export PYTHONPATH=${PYTHONPATH:-/root:/root/infra-ia}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Démarrage du service d'agents infra-ia sur le port $AGENTS_API_PORT"
echo "PYTHONPATH: $PYTHONPATH"

# Vérification des dépendances
echo "Vérification des dépendances..."
pip install -q fastapi uvicorn httpx pydantic

# Démarrage du service
echo "Démarrage du service..."
python3 api_service.py
