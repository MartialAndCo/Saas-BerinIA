from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.api import deps
from app.models.agent import Agent as AgentModel
from app.schemas.agent import Agent, AgentCreate, AgentUpdate
from app.schemas.agent_log import AgentLog, AgentLogCreate, AgentLogFeedback
from app.crud import agent as agent_crud
from app.crud import agent_log as log_crud
from app.models import User as UserModel

router = APIRouter(tags=["Agents"])

@router.get("/", response_model=List[Agent])
def get_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Récupère la liste des agents avec filtres optionnels
    """
    agents = agent_crud.get_agents(db=db, skip=skip, limit=limit, status=status)
    return agents

@router.post("/", response_model=Agent)
def create_agent(
    agent_in: AgentCreate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user),
):
    """
    Crée un nouvel agent avec configuration
    """
    agent = agent_crud.create(db=db, obj_in=agent_in)
    return agent

@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: int, db: Session = Depends(deps.get_db)):
    """
    Récupère un agent spécifique par son ID
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{id}", response_model=Agent)
def update_agent(
    id: int,
    agent_in: AgentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user),
):
    """
    Met à jour un agent existant
    """
    agent = agent_crud.get(db=db, id=id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_crud.update(db=db, db_obj=agent, obj_in=agent_in)
    return agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(deps.get_db)):
    """
    Supprime un agent
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_crud.remove(db=db, id=agent_id)
    return None

@router.post("/{agent_id}/restart", response_model=Agent)
def restart_agent(agent_id: int, db: Session = Depends(deps.get_db)):
    """
    Redémarre un agent en erreur
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.statut != "error":
        raise HTTPException(status_code=400, detail="Only agents in error state can be restarted")
    
    agent.statut = "active"
    agent_crud.update(db=db, db_obj=agent, obj_in={"statut": "active"})
    return agent

@router.get("/{agent_id}/logs", response_model=List[AgentLog])
def get_agent_logs(
    agent_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(deps.get_db)
):
    """
    Récupère les logs d'un agent spécifique
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    logs = log_crud.get_logs(db=db, agent_id=agent_id, skip=skip, limit=limit)
    return logs

@router.post("/{agent_id}/logs", response_model=AgentLog)
def create_agent_log(
    agent_id: int,
    log_data: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db)
):
    """
    Crée un nouvel enregistrement de log pour un agent
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Créer l'objet AgentLogCreate à partir des données
    log_create = AgentLogCreate(
        agent_id=agent_id,
        operation=log_data.get("operation", "execute"),
        status=log_data.get("status", "completed"),
        execution_time=log_data.get("execution_time", 0.0),
        input_data=log_data.get("input_data"),
        output_data=log_data.get("output_data")
    )
    
    log = log_crud.create(db=db, obj_in=log_create)
    return log

@router.post("/{agent_id}/logs/{log_id}/feedback", response_model=AgentLog)
def add_log_feedback(
    agent_id: int,
    log_id: int,
    feedback: AgentLogFeedback,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Ajoute un feedback à un log d'agent spécifique
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    log = log_crud.get(db=db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    if log.agent_id != agent_id:
        raise HTTPException(status_code=400, detail="Log does not belong to this agent")
    
    updated_log = log_crud.add_feedback(db=db, log_id=log_id, feedback=feedback)
    return updated_log

@router.get("/{agent_id}/feedback", response_model=Dict[str, Any])
def get_agent_feedback_stats(
    agent_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Récupère les statistiques de feedback pour un agent
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    stats = log_crud.get_feedback_stats(db=db, agent_id=agent_id)
    return stats

@router.post("/{agent_id}/configure", response_model=Agent)
def configure_agent(
    agent_id: int,
    configuration: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Configure un agent avec des paramètres spécifiques
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = {"configuration": configuration}
    updated_agent = agent_crud.update(db=db, db_obj=agent, obj_in=update_data)
    
    return updated_agent

@router.post("/{agent_id}/execute", response_model=Dict[str, Any])
async def execute_agent(
    agent_id: int,
    input_data: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db)
):
    """
    Exécute un agent avec les données d'entrée fournies via le service d'agents infra-ia
    """
    from app.services.agent_service import execute_agent as call_agent_service
    from datetime import datetime
    
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.statut != "active":
        raise HTTPException(status_code=400, detail="Agent must be active to execute")
    
    # Exécuter l'agent via notre service
    result = await call_agent_service(agent.type, input_data)
    
    # Mettre à jour l'agent
    update_data = {
        "derniere_execution": datetime.utcnow(),
        "statut": "active" if result.get("status") == "completed" else "error"
    }
    
    # Si des leads ont été générés, mettre à jour le compteur
    if result.get("status") == "completed" and "result" in result:
        agent_result = result["result"]
        if isinstance(agent_result, dict) and "leads_count" in agent_result:
            current_leads = agent.leads_generes or 0
            update_data["leads_generes"] = current_leads + agent_result["leads_count"]
    
    agent_crud.update(db=db, db_obj=agent, obj_in=update_data)
    
    # Créer un log pour cette exécution
    log_create = AgentLogCreate(
        agent_id=agent_id,
        operation="execute",
        status=result.get("status", "error"),
        execution_time=result.get("execution_time", 0.0),
        input_data=input_data,
        output_data=result
    )
    
    log_crud.create(db=db, obj_in=log_create)
    
    return result

@router.post("/{agent_id}/toggle", response_model=Agent)
def toggle_agent(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Active ou désactive un agent
    """
    agent = agent_crud.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_status = "inactive" if agent.statut == "active" else "active"
    updated_agent = agent_crud.update(db=db, db_obj=agent, obj_in={"statut": new_status})
    
    return updated_agent
