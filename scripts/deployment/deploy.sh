#!/bin/bash
# Script de déploiement pour l'infrastructure d'agents IA
# Usage: ./deploy.sh [--install-deps] [--systemd]

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PORT=8555
INSTALL_DEPS=0
SYSTEMD=0
REPORTS_DIR="logs/analytics_reports"
API_SCRIPT_PATH="/root/infra-ia/api_service.py"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/infra-ia-agents.service"

# Analyser les arguments
for arg in "$@"
do
    case $arg in
        --install-deps)
        INSTALL_DEPS=1
        shift
        ;;
        --systemd)
        SYSTEMD=1
        shift
        ;;
        *)
        # Ignorer l'argument inconnu
        shift
        ;;
    esac
done

# Message d'en-tête
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}      Déploiement de l'infrastructure IA      ${NC}"
echo -e "${BLUE}===============================================${NC}"

# Fonction pour l'installation des dépendances
install_deps() {
    echo -e "\n${YELLOW}Installation des dépendances Python...${NC}"
    pip install fastapi uvicorn httpx python-dotenv pydantic
    
    # Dépendances spécifiques pour les visualisations
    pip install matplotlib numpy
    
    echo -e "${GREEN}Dépendances installées avec succès.${NC}"
}

# Fonction pour créer les répertoires nécessaires
create_directories() {
    echo -e "\n${YELLOW}Création des répertoires...${NC}"
    mkdir -p logs
    mkdir -p $REPORTS_DIR
    mkdir -p prompts
    echo -e "${GREEN}Répertoires créés avec succès.${NC}"
}

# Fonction pour configurer systemd
setup_systemd() {
    echo -e "\n${YELLOW}Configuration du service systemd...${NC}"
    if [ -f "$SYSTEMD_SERVICE_FILE" ]; then
        echo -e "${YELLOW}Le fichier de service existe déjà, mise à jour...${NC}"
        systemctl stop infra-ia-agents || true
    fi
    
    # Créer le fichier de service
    cat > /tmp/infra-ia-agents.service << EOF
[Unit]
Description=Service d'agents IA pour Berinia
After=network.target

[Service]
User=root
WorkingDirectory=/root/infra-ia
ExecStart=/usr/bin/python3 $API_SCRIPT_PATH
Restart=on-failure
Environment="AGENTS_API_PORT=$PORT"

[Install]
WantedBy=multi-user.target
EOF

    # Installer et activer le service
    sudo mv /tmp/infra-ia-agents.service $SYSTEMD_SERVICE_FILE
    sudo systemctl daemon-reload
    sudo systemctl enable infra-ia-agents
    sudo systemctl start infra-ia-agents
    
    echo -e "${GREEN}Service systemd configuré et démarré.${NC}"
    echo -e "Vérifiez le statut avec: ${BLUE}systemctl status infra-ia-agents${NC}"
}

# Fonction pour tester l'API
test_api() {
    echo -e "\n${YELLOW}Test de l'API des agents...${NC}"
    echo -e "Patientez pendant le démarrage du serveur..."
    sleep 2
    
    # Tester l'API
    RESPONSE=$(curl -s http://localhost:$PORT/)
    if [[ $RESPONSE == *"running"* ]]; then
        echo -e "${GREEN}✓ L'API répond correctement.${NC}"
        echo -e "Réponse: $RESPONSE"
    else
        echo -e "${RED}✗ L'API ne répond pas correctement.${NC}"
        echo -e "Réponse: $RESPONSE"
        echo -e "Vérifiez les logs pour plus d'informations."
    fi
}

# Fonction pour tester un agent
test_analytics_agent() {
    echo -e "\n${YELLOW}Test de l'agent d'analyse...${NC}"
    
    # Exécuter le script de test
    echo -e "Exécution du script de test..."
    python test_analytics_agent.py
    
    # Vérifier les résultats
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test de l'agent d'analyse réussi.${NC}"
    else
        echo -e "${RED}✗ Test de l'agent d'analyse échoué.${NC}"
    fi
}

# Exécution principale
if [ $INSTALL_DEPS -eq 1 ]; then
    install_deps
fi

create_directories

# Vérifier si le script API existe
if [ ! -f "$API_SCRIPT_PATH" ]; then
    echo -e "${RED}Erreur: Le script API n'existe pas: $API_SCRIPT_PATH${NC}"
    exit 1
fi

# Vérifier les permissions d'exécution
if [ ! -x "$API_SCRIPT_PATH" ]; then
    echo -e "${YELLOW}Ajout des permissions d'exécution au script API...${NC}"
    chmod +x "$API_SCRIPT_PATH"
fi

# Tester l'agent avant le déploiement
test_analytics_agent

# Déployer avec systemd si demandé
if [ $SYSTEMD -eq 1 ]; then
    setup_systemd
    test_api
else
    echo -e "\n${YELLOW}Démarrage du serveur API en mode interactif...${NC}"
    echo -e "Appuyez sur Ctrl+C pour arrêter le serveur."
    python $API_SCRIPT_PATH
fi

echo -e "\n${GREEN}Déploiement terminé avec succès.${NC}"
echo -e "API disponible sur: ${BLUE}http://localhost:$PORT/${NC}"
echo -e "${BLUE}===============================================${NC}"
