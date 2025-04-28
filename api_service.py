import os
import time
import asyncio
from datetime import datetime
import threading
from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any, List, Optional
import uvicorn
import importlib
import logging
from pydantic import BaseModel

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agents-api")

app = FastAPI(title="Agents infra-ia API")

# Configuration des agents autonomes
AUTONOMOUS_AGENTS = {
    "brain": {
        "agent_type": "brain",
        "schedule": "hourly",  # Le cerveau évalue régulièrement la situation
        "input_data": {"operation": "evaluate_global_strategy"},
        "active": True,
        "priority": "highest"  # Indique que cet agent a la priorité sur tous les autres
    },
    "analytics": {
        "agent_type": "analytics",
        "schedule": "daily",  # daily, hourly, etc.
        "input_data": {"operation": "daily_analysis"},
        "active": True
    },
    "conductor": {
        "agent_type": "conductor",
        "schedule": "hourly",
        "input_data": {"operation": "orchestrate_pipeline"},
        "active": True
    },
    "cleaner": {
        "agent_type": "cleaner",
        "schedule": "daily",
        "input_data": {"operation": "clean_database"},
        "active": True
    }
}

# Gestion de l'état des jobs en cours
running_jobs = {}

# Mappage des types d'agents
AGENT_MAPPING = {
    "brain": "agents.controller.decision_brain_agent",  # Le cerveau décisionnel de plus haut niveau
    "scraper": "agents.scraper.apify_scraper",
    "analytics": "agents.analytics.analytics_agent", 
    "cleaner": "agents.cleaner.lead_cleaner",
    "pivot": "agents.pivot.pivot_decider",
    "messenger": "agents.messenger.messenger_agent",
    "conductor": "agents.controller.conductor_agent",
    "knowledge": "agents.knowledge.knowledge_injector_agent",
    "classifier": "agents.classifier.lead_classifier_agent",
    "crm": "agents.exporter.crm_exporter_agent",
    "campaign": "agents.controller.campaign_starter_agent"
}

# Classes des agents
AGENT_CLASSES = {
    "brain": "DecisionBrainAgent",  # Le cerveau décisionnel de plus haut niveau
    "scraper": "ApifyScraper",
    "analytics": "AnalyticsAgent", 
    "cleaner": "LeadCleaner",
    "pivot": "PivotDecider",
    "messenger": "MessengerAgent",
    "conductor": "ConductorAgent",
    "knowledge": "KnowledgeInjectorAgent",
    "classifier": "LeadClassifierAgent",
    "crm": "CRMExporterAgent",
    "campaign": "CampaignStarterAgent"
}

def get_agent_instance(agent_type: str):
    """Instancie un agent à partir de son type"""
    if agent_type not in AGENT_MAPPING:
        raise ValueError(f"Type d'agent non supporté: {agent_type}")
    
    # Utiliser directement un mock sans importer les modules
    class MockAgent:
        def run(self, input_data):
            logger.info(f"Simulation d'exécution de l'agent {agent_type} avec {input_data}")
            
            # Générer des résultats différents selon le type d'agent
            results = {
                "agent_type": agent_type,
                "input": input_data,
                "output": f"Résultat de l'agent {agent_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Ajouter des données spécifiques selon le type d'agent
            if agent_type == "analytics":
                results["metrics"] = {
                    "performance": 0.85,
                    "engagement": 0.76,
                    "conversion": 0.32
                }
                results["leads_count"] = 5
            elif agent_type == "scraper":
                results["found_leads"] = 28
                results["valid_leads"] = 25
                results["leads_count"] = 25
            elif agent_type == "cleaner":
                results["processed"] = 42
                results["cleaned"] = 38
                results["duplicates"] = 4
            
            return results
    
    # Retourner le mock
    return MockAgent()

@app.get("/")
async def root():
    """Endpoint racine pour vérifier que le service est en cours d'exécution"""
    return {"status": "running", "service": "infra-ia agents API"}

@app.get("/agents/types", response_model=List[str])
async def get_agent_types():
    """Retourne les types d'agents disponibles"""
    return list(AGENT_MAPPING.keys())

# Classes de modèles pour les endpoints
class AgentConfig(BaseModel):
    agent_type: str
    schedule: str
    input_data: Dict[str, Any]
    active: bool = True

class JobInfo(BaseModel):
    job_id: str
    agent_type: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# Fonctions de planification
def get_schedule_seconds(schedule: str) -> int:
    """Convertit un format de planification en secondes"""
    schedule_map = {
        "minute": 60,
        "hourly": 3600,
        "daily": 86400,
        "weekly": 604800
    }
    return schedule_map.get(schedule, 3600)  # Par défaut: horaire

def run_agent_job(agent_type: str, input_data: Dict[str, Any], job_id: str):
    """Exécute un agent dans un thread séparé et met à jour son statut"""
    try:
        # Marquer comme en cours d'exécution
        running_jobs[job_id]["status"] = "running"
        running_jobs[job_id]["start_time"] = datetime.utcnow().isoformat()
        
        # Exécuter l'agent
        logger.info(f"Démarrage de l'exécution autonome de l'agent {agent_type} (job {job_id})")
        start_time = time.time()
        agent = get_agent_instance(agent_type)
        result = agent.run(input_data)
        execution_time = time.time() - start_time
        
        # Mettre à jour le statut avec le résultat
        running_jobs[job_id]["status"] = "completed"
        running_jobs[job_id]["end_time"] = datetime.utcnow().isoformat()
        running_jobs[job_id]["result"] = {
            "status": "completed",
            "data": result,
            "execution_time": execution_time
        }
        
        logger.info(f"Agent {agent_type} exécuté avec succès (job {job_id}) en {execution_time:.2f}s")
        
    except Exception as e:
        # En cas d'erreur
        error_msg = str(e)
        logger.error(f"Erreur lors de l'exécution autonome de l'agent {agent_type} (job {job_id}): {error_msg}")
        
        running_jobs[job_id]["status"] = "error"
        running_jobs[job_id]["end_time"] = datetime.utcnow().isoformat()
        running_jobs[job_id]["result"] = {
            "status": "error",
            "error": error_msg
        }

async def schedule_agent(agent_name: str, config: Dict[str, Any]):
    """Planifie l'exécution récurrente d'un agent"""
    while True:
        if config.get("active", False):
            # Générer un ID unique pour cette exécution
            job_id = f"{agent_name}_{int(time.time())}"
            
            # Initialiser les informations de job
            running_jobs[job_id] = {
                "agent_type": config["agent_type"],
                "status": "scheduled",
                "start_time": None,
                "end_time": None,
                "result": None
            }
            
            # Exécuter l'agent dans un thread séparé
            thread = threading.Thread(
                target=run_agent_job,
                args=(config["agent_type"], config["input_data"], job_id)
            )
            thread.daemon = True
            thread.start()
            
            # Attendre selon la planification
            schedule_seconds = get_schedule_seconds(config["schedule"])
            logger.info(f"Agent {agent_name} planifié pour exécution dans {schedule_seconds} secondes")
        
        # Attendre jusqu'à la prochaine exécution
        schedule_seconds = get_schedule_seconds(config["schedule"])
        await asyncio.sleep(schedule_seconds)

@app.post("/agents/{agent_type}/execute")
async def execute_agent(
    agent_type: str,
    input_data: Dict[str, Any] = Body(...)
):
    """Exécute un agent avec les données d'entrée fournies"""
    try:
        start_time = time.time()
        agent = get_agent_instance(agent_type)
        result = agent.run(input_data)
        execution_time = time.time() - start_time
        
        return {
            "status": "completed",
            "result": result,
            "execution_time": execution_time
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Erreur lors de l'exécution de l'agent {agent_type}")
        return {
            "status": "error",
            "error": str(e),
            "execution_time": time.time() - start_time
        }

@app.get("/autonomous-agents", response_model=Dict[str, Any])
async def get_autonomous_agents():
    """Liste tous les agents autonomes configurés"""
    return {
        "agents": AUTONOMOUS_AGENTS,
        "running_jobs": running_jobs
    }

@app.post("/autonomous-agents/{agent_name}/configure")
async def configure_autonomous_agent(
    agent_name: str,
    config: AgentConfig
):
    """Configure un agent autonome"""
    if agent_name in AUTONOMOUS_AGENTS:
        AUTONOMOUS_AGENTS[agent_name] = config.dict()
        return {"status": "success", "message": f"Agent {agent_name} configuré avec succès"}
    else:
        # Créer un nouvel agent autonome
        AUTONOMOUS_AGENTS[agent_name] = config.dict()
        
        # Démarrer la planification si actif
        if config.active:
            asyncio.create_task(schedule_agent(agent_name, config.dict()))
        
        return {"status": "success", "message": f"Nouvel agent autonome {agent_name} créé"}

@app.post("/autonomous-agents/{agent_name}/toggle")
async def toggle_autonomous_agent(agent_name: str):
    """Active ou désactive un agent autonome"""
    if agent_name not in AUTONOMOUS_AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent autonome {agent_name} non trouvé")
    
    AUTONOMOUS_AGENTS[agent_name]["active"] = not AUTONOMOUS_AGENTS[agent_name]["active"]
    
    return {
        "status": "success", 
        "agent": agent_name, 
        "active": AUTONOMOUS_AGENTS[agent_name]["active"]
    }

@app.get("/jobs", response_model=Dict[str, JobInfo])
async def get_jobs():
    """Récupère la liste des jobs récents"""
    return running_jobs

@app.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str):
    """Récupère les détails d'un job spécifique"""
    if job_id not in running_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} non trouvé")
    
    return running_jobs[job_id]

# Démarrer les agents autonomes lors du lancement
@app.on_event("startup")
async def startup_event():
    """Initialise les tâches des agents autonomes au démarrage"""
    # D'abord, démarrer le DecisionBrainAgent (cerveau) en premier
    # car c'est lui qui doit analyser la situation et initier les décisions stratégiques
    if "brain" in AUTONOMOUS_AGENTS and AUTONOMOUS_AGENTS["brain"].get("active", True):
        brain_config = AUTONOMOUS_AGENTS["brain"]
        logger.info("🧠 Démarrage prioritaire du DecisionBrainAgent (cerveau du système)")
        brain_task = asyncio.create_task(schedule_agent("brain", brain_config))
        # Attendre que le cerveau effectue sa première exécution avant de démarrer les autres agents
        await asyncio.sleep(2)
        
    # Ensuite démarrer les autres agents
    for agent_name, config in AUTONOMOUS_AGENTS.items():
        if agent_name != "brain" and config.get("active", True):
            logger.info(f"Démarrage de l'agent autonome {agent_name}")
            asyncio.create_task(schedule_agent(agent_name, config))

if __name__ == "__main__":
    # Port défini par une variable d'environnement ou 8555 par défaut
    port = int(os.environ.get("AGENTS_API_PORT", 8555))
    
    # Logging au démarrage
    logger.info(f"Démarrage du service d'agents infra-ia sur le port {port}")
    
    # Lancer le serveur uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
