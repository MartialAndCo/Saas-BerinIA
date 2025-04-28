"""
Module pour la gestion de stockage des campagnes terminées.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Chemin vers le fichier de stockage des campagnes
CAMPAIGNS_FILE = os.path.join("db", "campaigns.json")

def ensure_storage_file():
    """Assure que le fichier de stockage existe et contient une structure JSON valide."""
    if not os.path.exists(CAMPAIGNS_FILE):
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(CAMPAIGNS_FILE), exist_ok=True)
        # Créer le fichier initial avec une structure valide
        with open(CAMPAIGNS_FILE, "w") as f:
            json.dump({
                "campaigns": [],
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    else:
        # Vérifier que le fichier contient du JSON valide
        try:
            with open(CAMPAIGNS_FILE, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            # Recréer avec une structure valide si le JSON est corrompu
            with open(CAMPAIGNS_FILE, "w") as f:
                json.dump({
                    "campaigns": [],
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

def save_campaign(campaign_data: Dict[str, Any]) -> bool:
    """
    Sauvegarde les données d'une campagne terminée.
    
    Args:
        campaign_data: Dictionnaire contenant les détails de la campagne
        
    Returns:
        bool: True si sauvegarde réussie, False sinon
    """
    try:
        ensure_storage_file()
        
        # Charger les données existantes
        with open(CAMPAIGNS_FILE, "r") as f:
            data = json.load(f)
            
        # Ajouter les métadonnées de stockage
        campaign_data["_storage_metadata"] = {
            "saved_at": datetime.now().isoformat(),
            "storage_id": f"storage_{int(time.time())}_{hash(str(campaign_data['campaign_id']))}"
        }
        
        # Vérifier si cette campagne existe déjà (basé sur campaign_id)
        campaign_id = campaign_data.get("campaign_id")
        exists = False
        
        for i, campaign in enumerate(data["campaigns"]):
            if campaign.get("campaign_id") == campaign_id:
                # Mettre à jour une campagne existante
                data["campaigns"][i] = campaign_data
                exists = True
                break
                
        if not exists:
            # Ajouter une nouvelle campagne
            data["campaigns"].append(campaign_data)
            
        # Mettre à jour le timestamp
        data["last_updated"] = datetime.now().isoformat()
        
        # Sauvegarder les données mises à jour
        with open(CAMPAIGNS_FILE, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"Campaign {campaign_id} saved successfully")
        return True
    except Exception as e:
        print(f"Error saving campaign: {str(e)}")
        return False
        
def get_all_campaigns() -> List[Dict[str, Any]]:
    """
    Récupère toutes les campagnes sauvegardées.
    
    Returns:
        Liste des campagnes
    """
    ensure_storage_file()
    
    try:
        with open(CAMPAIGNS_FILE, "r") as f:
            data = json.load(f)
        return data.get("campaigns", [])
    except Exception as e:
        print(f"Error loading campaigns: {str(e)}")
        return []
        
def get_campaign_by_id(campaign_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère une campagne spécifique par son ID.
    
    Args:
        campaign_id: ID de la campagne à récupérer
        
    Returns:
        Données de la campagne ou None si non trouvée
    """
    campaigns = get_all_campaigns()
    
    for campaign in campaigns:
        if campaign.get("campaign_id") == campaign_id:
            return campaign
            
    return None
    
def get_campaigns_by_niche(niche: str) -> List[Dict[str, Any]]:
    """
    Récupère les campagnes pour une niche spécifique.
    
    Args:
        niche: La niche à rechercher
        
    Returns:
        Liste des campagnes pour cette niche
    """
    campaigns = get_all_campaigns()
    
    # Filtrer les campagnes par niche (cas insensible)
    return [
        campaign for campaign in campaigns 
        if campaign.get("niche", "").lower() == niche.lower()
    ]

def get_active_campaigns() -> List[Dict[str, Any]]:
    """
    Récupère les campagnes actives (statut différent de COMPLETED/FAILED/ERROR).
    
    Returns:
        Liste des campagnes actives
    """
    campaigns = get_all_campaigns()
    
    # Filtrer pour ne garder que les campagnes actives
    return [
        campaign for campaign in campaigns
        if campaign.get("status") not in ["COMPLETED", "FAILED", "ERROR"]
    ]
    
def get_completed_campaigns() -> List[Dict[str, Any]]:
    """
    Récupère les campagnes terminées.
    
    Returns:
        Liste des campagnes terminées
    """
    campaigns = get_all_campaigns()
    
    # Filtrer pour ne garder que les campagnes terminées
    return [
        campaign for campaign in campaigns
        if campaign.get("status") == "COMPLETED"
    ]
