#!/usr/bin/env python3
"""
Script pour corriger l'erreur "'dict' object has no attribute '_sa_instance_state'"
dans les endpoints campaigns et niches de l'API Berinia.

Cette erreur se produit car nous avons remplacé des objets SQLAlchemy par des dictionnaires,
mais maintenant SQLAlchemy essaie d'accéder à des attributs ORM sur ces dictionnaires.
"""

import os
import sys
import re
import logging
from datetime import datetime

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-api-fix-dict")

# Chemins vers les fichiers Berinia
BERINIA_BACKEND_PATH = os.getenv("BERINIA_BACKEND_PATH", "/root/berinia/backend")
API_ENDPOINTS_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "api", "endpoints")

def check_paths():
    """Vérifier que les chemins existent"""
    if not os.path.exists(BERINIA_BACKEND_PATH):
        print(f"❌ Chemin backend Berinia introuvable: {BERINIA_BACKEND_PATH}")
        return False
    
    if not os.path.exists(API_ENDPOINTS_DIR):
        print(f"❌ Répertoire des endpoints introuvable: {API_ENDPOINTS_DIR}")
        return False
    
    return True

def fix_campaigns_endpoint():
    """
    Corriger l'erreur dans campaigns.py avec une approche plus robuste.
    
    Au lieu de modifier les objets directement, on utilise jsonable_encoder pour la sérialisation
    juste avant le retour de la fonction.
    """
    campaigns_path = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    if not os.path.exists(campaigns_path):
        print(f"❌ Fichier campaigns.py non trouvé à {campaigns_path}")
        return False
    
    print(f"\n🔧 Correction de l'erreur dict dans campaigns.py...")
    
    # Lire le fichier
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde si elle n'existe pas déjà
    backup_path = f"{campaigns_path}.dict.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Nouvelle approche : utiliser jsonable_encoder pour la sérialisation
    modified_content = content
    
    # Chercher les motifs potentiellement problématiques dans notre modification précédente
    patterns_to_replace = [
        r'campaign\.leads = \[{"id": lead\.id.*?for attr in.*?campaign_leads\.append\(lead_dict\).*?campaign\.leads = campaign_leads',
        r'if hasattr\(campaign, \'leads\'\) and campaign\.leads:.*?# Utiliser des objets dict.*?campaign\.leads = \[{"id": lead\.id.*?\]',
        r'if hasattr\(campaign, \'leads\'\) and campaign\.leads:.*?# Créer des copies des leads.*?campaign\.leads = \[{"id": lead\.id.*?\]',
        r'for campaign in campaigns:.*?if hasattr\(campaign, \'leads\'\) and campaign\.leads:.*?campaign\.leads = \[.*?\]'
    ]
    
    found_match = False
    for pattern in patterns_to_replace:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            found_match = True
            for match in matches:
                modified_content = modified_content.replace(match, "# Suppression du code de conversion problématique")
    
    if found_match:
        print(f"✅ Suppression des transformations problématiques dans campaigns.py")
    
    # Ajouter la sérialisation avec jsonable_encoder avant le retour
    functions_to_modify = re.findall(r'def\s+(get_campaigns?|read_campaigns?|read_all_campaigns?)\b.*?:.*?return\s+[^{]+', modified_content, re.DOTALL)
    
    if functions_to_modify:
        for func_text in functions_to_modify:
            # Extraire le nom de la fonction pour le logging
            func_name = re.search(r'def\s+(\w+)', func_text).group(1)
            
            # Trouver la ligne de retour
            return_match = re.search(r'(\s*)return\s+(.+?)(?:\s*$|\s*#)', func_text, re.DOTALL)
            if return_match:
                indent = return_match.group(1)
                return_var = return_match.group(2).strip()
                
                # Créer le code de sérialisation
                serialization_code = f"""
{indent}# Utiliser jsonable_encoder pour sérialiser les objets SQLAlchemy
{indent}from fastapi.encoders import jsonable_encoder
{indent}return jsonable_encoder({return_var})
"""
                
                # Remplacer la ligne de retour
                old_return = f"{indent}return {return_var}"
                modified_content = modified_content.replace(old_return, serialization_code)
                print(f"✅ Ajout de jsonable_encoder pour la fonction {func_name}")
    
    if modified_content != content:
        with open(campaigns_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à campaigns.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à campaigns.py")
        
        # Essayer une approche plus directe si aucune modification n'a été effectuée
        return apply_direct_fix_to_campaigns()

def fix_niches_endpoint():
    """
    Corriger l'erreur dans niches.py avec une approche plus robuste.
    
    Au lieu de modifier les objets directement, on utilise jsonable_encoder pour la sérialisation
    juste avant le retour de la fonction.
    """
    niches_path = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    if not os.path.exists(niches_path):
        print(f"❌ Fichier niches.py non trouvé à {niches_path}")
        return False
    
    print(f"\n🔧 Correction de l'erreur dict dans niches.py...")
    
    # Lire le fichier
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde si elle n'existe pas déjà
    backup_path = f"{niches_path}.dict.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Nouvelle approche : utiliser jsonable_encoder pour la sérialisation
    modified_content = content
    
    # Chercher les motifs potentiellement problématiques dans notre modification précédente
    patterns_to_replace = [
        r'campagne\.leads = \[{"id": lead\.id.*?for attr in.*?lead_dicts\.append\(lead_dict\).*?campagne\.leads = lead_dicts',
        r'if hasattr\(campagne, \'leads\'\) and campagne\.leads:.*?# Utiliser des objets dict.*?campagne\.leads = \[{"id": lead\.id.*?\]',
        r'if hasattr\(campagne, \'leads\'\) and campagne\.leads:.*?# Créer des copies des leads.*?campagne\.leads = \[{"id": lead\.id.*?\]',
        r'for niche in niches:.*?if hasattr\(niche, \'campagnes\'\):.*?for campagne in niche\.campagnes:.*?if hasattr\(campagne, \'leads\'\) and campagne\.leads:.*?campagne\.leads = \[.*?\]'
    ]
    
    found_match = False
    for pattern in patterns_to_replace:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            found_match = True
            for match in matches:
                modified_content = modified_content.replace(match, "# Suppression du code de conversion problématique")
    
    if found_match:
        print(f"✅ Suppression des transformations problématiques dans niches.py")
    
    # Ajouter la sérialisation avec jsonable_encoder avant le retour
    functions_to_modify = re.findall(r'def\s+(get_niches?|read_niches?|read_all_niches?)\b.*?:.*?return\s+[^{]+', modified_content, re.DOTALL)
    
    if functions_to_modify:
        for func_text in functions_to_modify:
            # Extraire le nom de la fonction pour le logging
            func_name = re.search(r'def\s+(\w+)', func_text).group(1)
            
            # Trouver la ligne de retour
            return_match = re.search(r'(\s*)return\s+(.+?)(?:\s*$|\s*#)', func_text, re.DOTALL)
            if return_match:
                indent = return_match.group(1)
                return_var = return_match.group(2).strip()
                
                # Créer le code de sérialisation
                serialization_code = f"""
{indent}# Utiliser jsonable_encoder pour sérialiser les objets SQLAlchemy
{indent}from fastapi.encoders import jsonable_encoder
{indent}return jsonable_encoder({return_var})
"""
                
                # Remplacer la ligne de retour
                old_return = f"{indent}return {return_var}"
                modified_content = modified_content.replace(old_return, serialization_code)
                print(f"✅ Ajout de jsonable_encoder pour la fonction {func_name}")
    
    if modified_content != content:
        with open(niches_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à niches.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à niches.py")
        
        # Essayer une approche plus directe si aucune modification n'a été effectuée
        return apply_direct_fix_to_niches()

def apply_direct_fix_to_campaigns():
    """
    Appliquer une correction directe au fichier campaigns.py.
    
    Cette fonction est utilisée si l'approche principale échoue.
    """
    campaigns_path = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Chercher les fonctions qui retournent des campagnes
    function_pattern = r'(def\s+(?:get_campaigns?|read_campaigns?|read_all_campaigns?)\b[^{]*?:)(.*?)(?=\s*def|\s*$)'
    function_matches = re.findall(function_pattern, content, re.DOTALL)
    
    modified_content = content
    for func_def, func_body in function_matches:
        # Chercher la ligne de retour
        return_match = re.search(r'(\s*)return\s+(.+?)(?:\s*$|\s*#)', func_body, re.DOTALL)
        if return_match:
            indent = return_match.group(1)
            return_var = return_match.group(2).strip()
            
            # Créer une version modifiée du corps de la fonction avec jsonable_encoder
            modified_body = re.sub(
                r'(\s*)return\s+(.+?)(?:\s*$|\s*#)',
                f'\\1from fastapi.encoders import jsonable_encoder\n\\1return jsonable_encoder({return_var})',
                func_body,
                flags=re.DOTALL
            )
            
            # Si le corps de fonction contient des modifications des objets leads,
            # supprimons ces modifications
            lead_mod_pattern = r'for\s+campaign\s+in\s+.+?:.*?if\s+hasattr\(campaign,\s*[\'"]leads[\'"]\).*?campaign\.leads\s*=\s*\[.*?\]'
            modified_body = re.sub(lead_mod_pattern, "# Code de modification des leads supprimé", modified_body, flags=re.DOTALL)
            
            # Remplacer la fonction entière
            modified_content = modified_content.replace(func_def + func_body, func_def + modified_body)
            print(f"✅ Modification directe de {func_def.split()[1].split('(')[0]}")
    
    if modified_content != content:
        with open(campaigns_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications directes appliquées à campaigns.py")
        return True
    else:
        # Approche alternative: remplacer complètement le fichier
        replacement_code = get_replacement_code_for_campaigns()
        with open(campaigns_path, 'w') as f:
            f.write(replacement_code)
        print(f"✅ Remplacement complet de campaigns.py")
        return True

def apply_direct_fix_to_niches():
    """
    Appliquer une correction directe au fichier niches.py.
    
    Cette fonction est utilisée si l'approche principale échoue.
    """
    niches_path = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Chercher les fonctions qui retournent des niches
    function_pattern = r'(def\s+(?:get_niches?|read_niches?|read_all_niches?)\b[^{]*?:)(.*?)(?=\s*def|\s*$)'
    function_matches = re.findall(function_pattern, content, re.DOTALL)
    
    modified_content = content
    for func_def, func_body in function_matches:
        # Chercher la ligne de retour
        return_match = re.search(r'(\s*)return\s+(.+?)(?:\s*$|\s*#)', func_body, re.DOTALL)
        if return_match:
            indent = return_match.group(1)
            return_var = return_match.group(2).strip()
            
            # Créer une version modifiée du corps de la fonction avec jsonable_encoder
            modified_body = re.sub(
                r'(\s*)return\s+(.+?)(?:\s*$|\s*#)',
                f'\\1from fastapi.encoders import jsonable_encoder\n\\1return jsonable_encoder({return_var})',
                func_body,
                flags=re.DOTALL
            )
            
            # Si le corps de fonction contient des modifications des objets leads,
            # supprimons ces modifications
            lead_mod_pattern = r'for\s+niche\s+in\s+.+?:.*?if\s+hasattr\(niche,\s*[\'"]campagnes[\'"]\).*?for\s+campagne\s+in\s+niche\.campagnes:.*?if\s+hasattr\(campagne,\s*[\'"]leads[\'"]\).*?campagne\.leads\s*=\s*\[.*?\]'
            modified_body = re.sub(lead_mod_pattern, "# Code de modification des leads supprimé", modified_body, flags=re.DOTALL)
            
            # Remplacer la fonction entière
            modified_content = modified_content.replace(func_def + func_body, func_def + modified_body)
            print(f"✅ Modification directe de {func_def.split()[1].split('(')[0]}")
    
    if modified_content != content:
        with open(niches_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications directes appliquées à niches.py")
        return True
    else:
        # Approche alternative: remplacer complètement le fichier
        replacement_code = get_replacement_code_for_niches()
        with open(niches_path, 'w') as f:
            f.write(replacement_code)
        print(f"✅ Remplacement complet de niches.py")
        return True

def get_replacement_code_for_campaigns():
    """
    Code de remplacement pour campaigns.py.
    
    Cette fonction est utilisée en dernier recours si toutes les autres approches échouent.
    """
    return """from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.api import deps
from app.models.campaign import Campaign
from app.schemas.campaign import Campaign as CampaignSchema
from app.crud.campaign import create_campaign, get_campaign_by_id, get_campaigns

router = APIRouter()

@router.post("/", response_model=CampaignSchema)
def create_campaign_endpoint(
    campaign: CampaignSchema,
    db: Session = Depends(deps.get_db)
):
    # Créer une nouvelle campagne.
    db_campaign = create_campaign(db=db, campaign=campaign)
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(db_campaign)

@router.get("/{campaign_id}", response_model=CampaignSchema)
def read_campaign(
    campaign_id: int,
    db: Session = Depends(deps.get_db)
):
    # Obtenir une campagne par son ID.
    db_campaign = get_campaign_by_id(db=db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(db_campaign)

@router.get("/", response_model=List[CampaignSchema])
def read_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    # Obtenir toutes les campagnes.
    campaigns = get_campaigns(db, skip=skip, limit=limit)
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(campaigns)
"""

def get_replacement_code_for_niches():
    """
    Code de remplacement pour niches.py.
    
    Cette fonction est utilisée en dernier recours si toutes les autres approches échouent.
    """
    return """from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.api import deps
from app.models.niche import Niche
from app.schemas.niche import Niche as NicheSchema
from app.crud.niche import create_niche, get_niche_by_id, get_niches

router = APIRouter()

@router.post("/", response_model=NicheSchema)
def create_niche_endpoint(
    niche: NicheSchema,
    db: Session = Depends(deps.get_db)
):
    # Créer une nouvelle niche.
    db_niche = create_niche(db=db, niche=niche)
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(db_niche)

@router.get("/{niche_id}", response_model=NicheSchema)
def read_niche(
    niche_id: int,
    db: Session = Depends(deps.get_db)
):
    # Obtenir une niche par son ID.
    db_niche = get_niche_by_id(db=db, niche_id=niche_id)
    if db_niche is None:
        raise HTTPException(status_code=404, detail="Niche non trouvée")
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(db_niche)

@router.get("/", response_model=List[NicheSchema])
def read_niches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    # Obtenir toutes les niches.
    niches = get_niches(db, skip=skip, limit=limit)
    # Utiliser jsonable_encoder pour sérialiser avant de retourner
    return jsonable_encoder(niches)
"""

def add_generic_orm_to_dict_converter():
    """
    Ajouter une fonction utilitaire pour convertir les objets SQLAlchemy en dictionnaires de manière générique.
    
    Cette fonction est utilisée si le problème persiste malgré les autres corrections.
    """
    utils_path = os.path.join(BERINIA_BACKEND_PATH, "app", "api", "utils")
    if not os.path.exists(utils_path):
        os.makedirs(utils_path)
    
    serializer_path = os.path.join(utils_path, "serializer.py")
    
    # Créer ou mettre à jour le fichier serializer.py
    serializer_code = '''from typing import Any, Dict, List, Union
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute

def sqlalchemy_to_dict(obj: Any) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
    """
    Convertit un objet SQLAlchemy en dictionnaire JSON-compatible.
    
    Args:
        obj: Un objet SQLAlchemy, une liste d'objets SQLAlchemy ou toute autre valeur
        
    Returns:
        Un dictionnaire, une liste de dictionnaires ou la valeur originale si elle n'est pas un objet SQLAlchemy
    """
    if isinstance(obj, list):
        return [sqlalchemy_to_dict(item) for item in obj]
    
    if isinstance(obj, dict):
        return {key: sqlalchemy_to_dict(value) for key, value in obj.items()}
    
    # Vérifier si c'est un objet SQLAlchemy
    if hasattr(obj, "__class__") and hasattr(obj.__class__, "__mapper__"):
        result = {}
        for key in obj.__mapper__.c.keys():
            value = getattr(obj, key)
            result[key] = sqlalchemy_to_dict(value)
            
        # Traiter les relations
        for relationship in obj.__mapper__.relationships:
            value = getattr(obj, relationship.key)
            if value is not None:
                result[relationship.key] = sqlalchemy_to_dict(value)
                
        return result
        
    # Si c'est une valeur primitive, la retourner telle quelle
    return obj
'''
    
    with open(serializer_path, 'w') as f:
        f.write(serializer_code)
    
    print(f"✅ Fonction de sérialisation générique créée: {serializer_path}")
    
    # Créer un fichier __init__.py s'il n'existe pas
    init_path = os.path.join(utils_path, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("# Module utils pour l'API\n")
    
    # Modifier campaigns.py et niches.py pour utiliser cette fonction
    campaigns_path = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    if os.path.exists(campaigns_path):
        with open(campaigns_path, 'r') as f:
            content = f.read()
        
        # Ajouter l'import
        if "from app.api.utils.serializer import sqlalchemy_to_dict" not in content:
            # Trouver les autres imports
            import_section_end = content.find("\n\nrouter = ")
            if import_section_end == -1:
                import_section_end = content.find("\nrouter = ")
            
            if import_section_end != -1:
                modified_content = content[:import_section_end] + "\nfrom app.api.utils.serializer import sqlalchemy_to_dict" + content[import_section_end:]
                
                # Remplacer les retours de fonctions
                function_pattern = r'def\s+(get_campaigns?|read_campaigns?|read_all_campaigns?)\b.*?return\s+([^{]+)'
                for func_match in re.finditer(function_pattern, modified_content, re.DOTALL):
                    func_name = func_match.group(1)
                    return_var = func_match.group(2).strip()
                    old_return = f"return {return_var}"
                    new_return = f"return sqlalchemy_to_dict({return_var})"
                    modified_content = modified_content.replace(old_return, new_return)
                
                with open(campaigns_path, 'w') as f:
                    f.write(modified_content)
                print(f"✅ Ajout de la fonction sqlalchemy_to_dict à campaigns.py")
    
    niches_path = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    if os.path.exists(niches_path):
        with open(niches_path, 'r') as f:
            content = f.read()
        
        # Ajouter l'import
        if "from app.api.utils.serializer import sqlalchemy_to_dict" not in content:
            # Trouver les autres imports
            import_section_end = content.find("\n\nrouter = ")
            if import_section_end == -1:
                import_section_end = content.find("\nrouter = ")
            
            if import_section_end != -1:
                modified_content = content[:import_section_end] + "\nfrom app.api.utils.serializer import sqlalchemy_to_dict" + content[import_section_end:]
                
                # Remplacer les retours de fonctions
                function_pattern = r'def\s+(get_niches?|read_niches?|read_all_niches?)\b.*?return\s+([^{]+)'
                for func_match in re.finditer(function_pattern, modified_content, re.DOTALL):
                    func_name = func_match.group(1)
                    return_var = func_match.group(2).strip()
                    old_return = f"return {return_var}"
                    new_return = f"return sqlalchemy_to_dict({return_var})"
                    modified_content = modified_content.replace(old_return, new_return)
                
                with open(niches_path, 'w') as f:
                    f.write(modified_content)
                print(f"✅ Ajout de la fonction sqlalchemy_to_dict à niches.py")
    
    return True

def restart_berinia_server():
    """Suggérer le redémarrage du serveur Berinia"""
    print(f"\n{'='*50}")
    print(f"🚀 REDÉMARRAGE REQUIS")
    print(f"{'='*50}")
    print("Pour appliquer toutes les corrections, veuillez:")
    print("1. Redémarrer le serveur Berinia avec la commande:")
    print("   sudo systemctl restart berinia-api.service")
    print("2. Redémarrer les agents infra-ia:")
    print("   python3 start_brain_agent.py")

def main():
    print(f"\n{'='*50}")
    print(f"🔧 CORRECTION DE L'ERREUR DICT DANS BERINIA")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    if not check_paths():
        print("❌ Vérification des chemins échouée. Veuillez vérifier les chemins d'accès.")
        return False
    
    # 1. Corriger les endpoints
    campaigns_fixed = fix_campaigns_endpoint()
    niches_fixed = fix_niches_endpoint()
    
    # 2. Si les méthodes précédentes ne suffisent pas, ajouter un convertisseur générique
    if not campaigns_fixed or not niches_fixed:
        print("\n⚠️ Les corrections directes n'ont pas fonctionné, ajout d'un convertisseur générique...")
        add_generic_orm_to_dict_converter()
    
    # 3. Suggérer le redémarrage
    restart_berinia_server()
    
    print(f"\n✅ Toutes les corrections possibles ont été appliquées.")
    return True

if __name__ == "__main__":
    main()
