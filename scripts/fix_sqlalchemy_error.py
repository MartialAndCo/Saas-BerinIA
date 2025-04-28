#!/usr/bin/env python3
"""
Script pour corriger l'erreur "'int' object has no attribute '_sa_instance_state'"
dans les endpoints campaigns et niches de l'API Berinia.

Cette erreur se produit car nous avons remplacé des objets SQLAlchemy par des entiers simples,
mais le framework essaie d'accéder à des attributs spécifiques d'SQLAlchemy sur ces entiers.
"""

import os
import sys
import re
import logging
from datetime import datetime

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-api-fix-sqlalchemy")

# Chemins vers les fichiers Berinia
BERINIA_BACKEND_PATH = os.getenv("BERINIA_BACKEND_PATH", "/root/berinia/backend")
API_ENDPOINTS_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "api", "endpoints")
BERINIA_SCHEMAS_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "schemas")

def check_paths():
    """Vérifier que les chemins existent"""
    if not os.path.exists(BERINIA_BACKEND_PATH):
        print(f"❌ Chemin backend Berinia introuvable: {BERINIA_BACKEND_PATH}")
        return False
    
    if not os.path.exists(API_ENDPOINTS_DIR):
        print(f"❌ Répertoire des endpoints introuvable: {API_ENDPOINTS_DIR}")
        return False
    
    return True

def fix_sqlalchemy_issue_in_campaigns():
    """
    Corriger l'erreur SQLAlchemy dans l'endpoint campaigns.py.
    
    L'erreur se produit car nous avons remplacé des objets Lead par des entiers simples,
    mais il existe encore du code qui essaie d'accéder à des attributs d'objets SQLAlchemy.
    """
    campaigns_path = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    if not os.path.exists(campaigns_path):
        print(f"❌ Fichier campaigns.py non trouvé à {campaigns_path}")
        return False
    
    print(f"\n🔧 Correction de l'erreur SQLAlchemy dans campaigns.py...")
    
    # Lire le fichier
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{campaigns_path}.sqlalchemy.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Au lieu de convertir les leads en IDs, nous allons utiliser une approche différente:
    # 1. Créer une nouvelle liste d'objets dans le format attendu par le schéma
    # 2. Utiliser jsonable_encoder ou similaire pour convertir ces objets en JSON-compatible
    
    lines = content.split('\n')
    modified_content = content
    
    # Chercher notre code précédent qui convertit les leads en IDs
    bad_code_pattern = r'# Conversion des leads en IDs.*?campaign\.leads = \[lead\.id for lead in campaign\.leads\]'
    bad_code_match = re.search(bad_code_pattern, content, re.DOTALL)
    
    if bad_code_match:
        bad_code = bad_code_match.group(0)
        # Remplacer par une approche qui utilise jsonable_encoder
        fixed_code = """# Préparation des données pour la sérialisation
    from fastapi.encoders import jsonable_encoder
    # Utiliser des objets dict avec uniquement les attributs nécessaires
    for campaign in campaigns:
        if hasattr(campaign, 'leads') and campaign.leads:
            # Créer des copies des leads avec uniquement les attributs nécessaires
            campaign.leads = [{"id": lead.id, "nom": lead.nom if hasattr(lead, 'nom') else None} for lead in campaign.leads]"""
        
        # Remplacer le code problématique
        modified_content = modified_content.replace(bad_code, fixed_code)
        print(f"✅ Correction de la méthode de sérialisation des leads dans campaigns.py")
    
    # Si notre approche précédente n'est pas trouvée, chercher et modifier les autres patterns similaires
    if modified_content == content:
        # Chercher d'autres patterns similaires
        lead_conversion_pattern = r'for campaign in ([a-zA-Z0-9_]+):.*?if hasattr\(campaign, \'leads\'\).*?campaign\.leads = \[lead\.id for lead in campaign\.leads\]'
        matches = re.findall(lead_conversion_pattern, content, re.DOTALL)
        
        if matches:
            for var_name in matches:
                pattern = f"for campaign in {var_name}:.*?if hasattr\(campaign, 'leads'\).*?campaign\.leads = \[lead\.id for lead in campaign\.leads\]"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    original_code = match.group(0)
                    
                    # Créer le code de remplacement
                    replacement_code = f"""for campaign in {var_name}:
        if hasattr(campaign, 'leads') and campaign.leads:
            # Utiliser des objets dict pour représenter les leads
            campaign_leads = []
            for lead in campaign.leads:
                # Créer un dictionnaire avec les attributs essentiels
                lead_dict = {{"id": lead.id}}
                for attr in ['nom', 'email', 'phone', 'status']:
                    if hasattr(lead, attr):
                        lead_dict[attr] = getattr(lead, attr)
                campaign_leads.append(lead_dict)
            campaign.leads = campaign_leads"""
                    
                    # Appliquer le remplacement
                    modified_content = modified_content.replace(original_code, replacement_code)
                    print(f"✅ Modification de la conversion des leads dans la boucle utilisant {var_name}")
        
        # Si aucun des patterns ci-dessus n'est trouvé, essayer une approche plus générique
        if modified_content == content:
            # Chercher les fonctions qui renvoient des campagnes
            function_pattern = r'def (get_campaigns?|read_campaigns?)\b[^{]*?:\s*(.*?)(?=\s*def|\s*$)'
            function_matches = re.findall(function_pattern, content, re.DOTALL)
            
            for func_name, func_body in function_matches:
                if 'return' in func_body and 'leads' in func_body:
                    # Trouver la ligne de retour
                    return_pattern = r'(\s*)return\s+(.+)'
                    return_match = re.search(return_pattern, func_body)
                    if return_match:
                        indent = return_match.group(1)
                        return_var = return_match.group(2).strip()
                        
                        # Créer le code pour prétraiter les données avant le retour
                        preprocessing_code = f"""{indent}# Préparation pour la sérialisation
{indent}from fastapi.encoders import jsonable_encoder
{indent}for item in {return_var}:
{indent}    if hasattr(item, 'leads') and item.leads:
{indent}        leads_dicts = []
{indent}        for lead in item.leads:
{indent}            lead_dict = {{"id": lead.id}}
{indent}            # Ajouter d'autres attributs selon le schéma
{indent}            for attr in ['nom', 'email', 'phone', 'status']:
{indent}                if hasattr(lead, attr):
{indent}                    lead_dict[attr] = getattr(lead, attr)
{indent}            leads_dicts.append(lead_dict)
{indent}        item.leads = leads_dicts
"""
                        
                        # Remplacer la fonction entière
                        original_func = f"def {func_name}:{func_body}"
                        modified_func = f"def {func_name}:{func_body.replace(f'{indent}return {return_var}', f'{preprocessing_code}{indent}return {return_var}')}"
                        modified_content = modified_content.replace(original_func, modified_func)
                        print(f"✅ Ajout du prétraitement de sérialisation avant le retour dans {func_name}")
    
    # Enregistrer les modifications
    if modified_content != content:
        with open(campaigns_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à campaigns.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à campaigns.py")
        
        # Une approche plus directe: modifier les schémas
        return fix_campaign_schema()

def fix_sqlalchemy_issue_in_niches():
    """
    Corriger l'erreur SQLAlchemy dans l'endpoint niches.py.
    
    L'erreur se produit car nous avons remplacé des objets Lead par des entiers simples,
    mais il existe encore du code qui essaie d'accéder à des attributs d'objets SQLAlchemy.
    """
    niches_path = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    if not os.path.exists(niches_path):
        print(f"❌ Fichier niches.py non trouvé à {niches_path}")
        return False
    
    print(f"\n🔧 Correction de l'erreur SQLAlchemy dans niches.py...")
    
    # Lire le fichier
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{niches_path}.sqlalchemy.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Utiliser la même approche que pour campaigns.py
    lines = content.split('\n')
    modified_content = content
    
    # Chercher notre code précédent qui convertit les leads en IDs
    bad_code_pattern = r'# Conversion des leads en IDs.*?campagne\.leads = \[lead\.id for lead in campagne\.leads\]'
    bad_code_match = re.search(bad_code_pattern, content, re.DOTALL)
    
    if bad_code_match:
        bad_code = bad_code_match.group(0)
        # Remplacer par une approche qui utilise jsonable_encoder
        fixed_code = """# Préparation des données pour la sérialisation
    from fastapi.encoders import jsonable_encoder
    # Utiliser des objets dict avec uniquement les attributs nécessaires
    for niche in niches:
        if hasattr(niche, 'campagnes'):  # Vérifier si la niche a des campagnes
            for campagne in niche.campagnes:  # Pour chaque campagne
                if hasattr(campagne, 'leads') and campagne.leads:  # Si la campagne a des leads
                    # Créer des copies des leads avec uniquement les attributs nécessaires
                    lead_dicts = []
                    for lead in campagne.leads:
                        lead_dict = {"id": lead.id}
                        # Ajouter d'autres attributs selon le schéma
                        for attr in ['nom', 'email', 'phone', 'status']:
                            if hasattr(lead, attr):
                                lead_dict[attr] = getattr(lead, attr)
                        lead_dicts.append(lead_dict)
                    campagne.leads = lead_dicts"""
        
        # Remplacer le code problématique
        modified_content = modified_content.replace(bad_code, fixed_code)
        print(f"✅ Correction de la méthode de sérialisation des leads dans niches.py")
    
    # Si notre approche précédente n'est pas trouvée, chercher et modifier les autres patterns similaires
    if modified_content == content:
        # Chercher d'autres patterns similaires
        lead_conversion_pattern = r'for niche in ([a-zA-Z0-9_]+):.*?if hasattr\(niche, \'campagnes\'\).*?campagne\.leads = \[lead\.id for lead in campagne\.leads\]'
        matches = re.findall(lead_conversion_pattern, content, re.DOTALL)
        
        if matches:
            for var_name in matches:
                pattern = f"for niche in {var_name}:.*?if hasattr\(niche, 'campagnes'\).*?campagne\.leads = \[lead\.id for lead in campagne\.leads\]"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    original_code = match.group(0)
                    
                    # Créer le code de remplacement
                    replacement_code = f"""for niche in {var_name}:
        if hasattr(niche, 'campagnes'):
            for campagne in niche.campagnes:
                if hasattr(campagne, 'leads') and campagne.leads:
                    # Utiliser des objets dict pour représenter les leads
                    lead_dicts = []
                    for lead in campagne.leads:
                        lead_dict = {{"id": lead.id}}
                        # Ajouter d'autres attributs selon le schéma
                        for attr in ['nom', 'email', 'phone', 'status']:
                            if hasattr(lead, attr):
                                lead_dict[attr] = getattr(lead, attr)
                        lead_dicts.append(lead_dict)
                    campagne.leads = lead_dicts"""
                    
                    # Appliquer le remplacement
                    modified_content = modified_content.replace(original_code, replacement_code)
                    print(f"✅ Modification de la conversion des leads dans la boucle utilisant {var_name}")
    
    # Enregistrer les modifications
    if modified_content != content:
        with open(niches_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à niches.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à niches.py")
        
        # Une approche plus directe: modifier les schémas
        return fix_niche_schema()

def fix_campaign_schema():
    """
    Corriger le schéma de Campaign pour qu'il accepte les IDs au lieu des objets Lead.
    """
    schema_path = os.path.join(BERINIA_SCHEMAS_DIR, "campaign.py")
    if not os.path.exists(schema_path):
        print(f"❌ Fichier schema campaign.py non trouvé à {schema_path}")
        return False
    
    print(f"\n🔧 Modification du schéma Campaign pour accepter les IDs...")
    
    # Lire le fichier
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{schema_path}.schema.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Chercher les définitions de classe qui contiennent le champ leads
    leads_field_pattern = r'(\s+leads\s*:.+)'
    matches = re.findall(leads_field_pattern, content)
    
    if matches:
        modified_content = content
        for match in matches:
            if "List[Lead]" in match:
                # Remplacer List[Lead] par List[int] pour accepter des IDs
                new_match = match.replace("List[Lead]", "List[int]")
                modified_content = modified_content.replace(match, new_match)
                print(f"✅ Modification du type leads dans le schéma Campaign")
            elif "List[int]" in match:
                # Déjà corrigé
                print(f"✅ Le schéma Campaign utilise déjà List[int] pour leads")
        
        # Enregistrer les modifications
        if modified_content != content:
            with open(schema_path, 'w') as f:
                f.write(modified_content)
            print(f"✅ Modifications appliquées au schéma Campaign")
            return True
        else:
            print(f"⚠️ Aucune modification appliquée au schéma Campaign")
    
    return False

def fix_niche_schema():
    """
    Corriger les schémas liés aux niches pour qu'ils fonctionnent correctement avec les IDs.
    """
    schema_path = os.path.join(BERINIA_SCHEMAS_DIR, "niche.py")
    if not os.path.exists(schema_path):
        print(f"❌ Fichier schema niche.py non trouvé à {schema_path}")
        return False
    
    print(f"\n🔧 Modification du schéma Niche pour le rendre compatible...")
    
    # Lire le fichier
    with open(schema_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{schema_path}.schema.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Chercher les mentions de leads dans le schéma
    leads_pattern = r'leads\s*:'
    if re.search(leads_pattern, content):
        print(f"✅ Le schéma Niche contient des références aux leads, vérification plus approfondie...")
        
        # Chercher si Campaign est défini dans ce fichier
        campaign_class_pattern = r'class\s+Campaign.*?:'
        campaign_matches = re.findall(campaign_class_pattern, content)
        
        modified_content = content
        changes_made = False
        
        if campaign_matches:
            # Il y a une classe Campaign dans le fichier niche.py, vérifier ses propriétés
            for campaign_class in campaign_matches:
                # Chercher le champ leads
                campaign_section = content.split(campaign_class)[1].split("class")[0] if "class" in content.split(campaign_class)[1] else content.split(campaign_class)[1]
                leads_field_pattern = r'(\s+leads\s*:.+)'
                leads_matches = re.findall(leads_field_pattern, campaign_section)
                
                if leads_matches:
                    for match in leads_matches:
                        if "List[Lead]" in match:
                            # Remplacer List[Lead] par List[int]
                            new_match = match.replace("List[Lead]", "List[int]")
                            modified_content = modified_content.replace(match, new_match)
                            print(f"✅ Modification du type leads dans la classe Campaign du schéma Niche")
                            changes_made = True
                        elif "List[int]" in match:
                            print(f"✅ La classe Campaign dans le schéma Niche utilise déjà List[int] pour leads")
        
        # Enregistrer les modifications
        if changes_made:
            with open(schema_path, 'w') as f:
                f.write(modified_content)
            print(f"✅ Modifications appliquées au schéma Niche")
            return True
        else:
            print(f"⚠️ Aucune modification nécessaire au schéma Niche")
    else:
        print(f"⚠️ Le schéma Niche ne contient pas de références directes aux leads")
    
    return False

def add_type_hints_to_models():
    """
    Ajouter des indications de type explicites aux modèles pour aider la sérialisation.
    """
    lead_model_path = os.path.join(BERINIA_BACKEND_PATH, "app", "models", "lead.py")
    
    if not os.path.exists(lead_model_path):
        print(f"❌ Fichier modèle lead.py non trouvé à {lead_model_path}")
        # Chercher d'autres emplacements possibles
        for root, dirs, files in os.walk(os.path.join(BERINIA_BACKEND_PATH, "app", "models")):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        if "class Lead" in content:
                            lead_model_path = os.path.join(root, file)
                            print(f"✅ Modèle Lead trouvé dans {lead_model_path}")
                            break
    
    if not os.path.exists(lead_model_path):
        print(f"❌ Impossible de trouver le modèle Lead dans le projet")
        return False
    
    print(f"\n🔧 Ajout d'indications de type au modèle Lead...")
    
    # Lire le fichier
    with open(lead_model_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{lead_model_path}.model.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Ajouter une méthode to_dict ou __json__ pour aider à la sérialisation
    lead_class_pattern = r'class\s+Lead\b.*?:'
    lead_class_match = re.search(lead_class_pattern, content)
    
    if lead_class_match:
        # Trouver la fin de la classe Lead
        lead_class_start = lead_class_match.start()
        next_class_match = re.search(r'class\s+\w+\b', content[lead_class_start+1:])
        
        if next_class_match:
            lead_class_end = lead_class_start + 1 + next_class_match.start()
        else:
            lead_class_end = len(content)
        
        lead_class_content = content[lead_class_start:lead_class_end]
        
        # Vérifier si la classe a déjà une méthode to_dict ou __json__
        if not re.search(r'def\s+(to_dict|__json__)', lead_class_content):
            # Déterminer l'indentation
            indent_match = re.search(r'(\s+)', lead_class_content)
            indent = indent_match.group(1) if indent_match else "    "
            
            # Créer la méthode to_dict
            to_dict_method = f"""
{indent}def to_dict(self):
{indent}    \"\"\"Convertir l'objet Lead en dictionnaire pour la sérialisation.\"\"\"
{indent}    return {{
{indent}        "id": self.id,
{indent}        "nom": self.nom if hasattr(self, 'nom') else None,
{indent}        "email": self.email if hasattr(self, 'email') else None,
{indent}        "phone": self.phone if hasattr(self, 'phone') else None,
{indent}        "status": self.status if hasattr(self, 'status') else None
{indent}    }}
"""
            
            # Ajouter la méthode à la fin de la classe
            modified_content = content[:lead_class_end] + to_dict_method + content[lead_class_end:]
            
            # Enregistrer les modifications
            with open(lead_model_path, 'w') as f:
                f.write(modified_content)
            
            print(f"✅ Méthode to_dict ajoutée à la classe Lead")
            return True
        else:
            print(f"✅ La classe Lead possède déjà une méthode de sérialisation")
    else:
        print(f"❌ Impossible de trouver la définition de la classe Lead dans {lead_model_path}")
    
    return False

def modify_model_relationship():
    """
    Modifier la relation dans le modèle Campaign pour utiliser une stratégie de chargement différente.
    """
    campaign_model_path = None
    
    # Chercher le fichier du modèle Campaign
    for root, dirs, files in os.walk(os.path.join(BERINIA_BACKEND_PATH, "app", "models")):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "class Campaign" in content and "lead" in content.lower():
                        campaign_model_path = file_path
                        print(f"✅ Modèle Campaign trouvé dans {campaign_model_path}")
                        break
        if campaign_model_path:
            break
    
    if not campaign_model_path:
        print(f"❌ Impossible de trouver le modèle Campaign dans le projet")
        return False
    
    print(f"\n🔧 Modification de la relation dans le modèle Campaign...")
    
    # Lire le fichier
    with open(campaign_model_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{campaign_model_path}.relation.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Chercher la relation leads
    leads_relation_pattern = r'leads\s*=\s*relationship\('
    leads_relation_match = re.search(leads_relation_pattern, content)
    
    if leads_relation_match:
        # Trouver la définition complète de la relation
        lead_relation_start = leads_relation_match.start()
        lead_relation_end = content.find(")", lead_relation_start) + 1
        
        relation_definition = content[lead_relation_start:lead_relation_end]
        
        # Vérifier si la relation contient déjà l'attribut lazy="selectin"
        if "lazy=" not in relation_definition or "lazy=\"selectin\"" not in relation_definition:
            # Modifier la relation pour utiliser lazy="selectin"
            if ")" in relation_definition:
                new_relation = relation_definition.replace(")", ", lazy=\"selectin\")")
                modified_content = content.replace(relation_definition, new_relation)
                
                # Enregistrer les modifications
                with open(campaign_model_path, 'w') as f:
                    f.write(modified_content)
                
                print(f"✅ Stratégie de chargement modifiée pour la relation leads dans Campaign")
                return True
            else:
                print(f"❌ Format de relation non reconnu: {relation_definition}")
        else:
            print(f"✅ La relation leads utilise déjà lazy=\"selectin\"")
    else:
        print(f"❌ Relation leads non trouvée dans le modèle Campaign")
    
    return False

def restart_berinia_server():
    """Suggérer le redémarrage du serveur Berinia"""
    print(f"\n{'='*50}")
    print(f"🚀 REDÉMARRAGE REQUIS")
    print(f"{'='*50}")
    print("Pour appliquer toutes les corrections, veuillez:")
    print("1. Redémarrer le serveur Berinia avec la commande appropriée")
    print("2. Redémarrer les agents infra-ia:")
    print("   python3 start_brain_agent.py")
    
    # Chercher un script de démarrage potentiel
    start_script = os.path.join(BERINIA_BACKEND_PATH, "start.sh")
    if os.path.exists(start_script):
        print(f"\nCommande suggérée: bash {start_script}")

def main():
    print(f"\n{'='*50}")
    print(f"🔧 CORRECTION DE L'ERREUR SQLALCHEMY DANS BERINIA")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    if not check_paths():
        print("❌ Vérification des chemins échouée. Veuillez vérifier les chemins d'accès.")
        return False
    
    # 1. Modifier les endpoints pour éviter le problème
    campaigns_fixed = fix_sqlalchemy_issue_in_campaigns()
    niches_fixed = fix_sqlalchemy_issue_in_niches()
    
    # 2. Si les modifications directes ne sont pas possibles, essayer d'autres approches
    if not campaigns_fixed or not niches_fixed:
        # Modifier les schémas de données
        schema_fixed = fix_campaign_schema() and fix_niche_schema()
        
        # Ajouter des méthodes de sérialisation aux modèles
        model_fixed = add_type_hints_to_models()
        
        # Modifier les relations des modèles
        relationship_fixed = modify_model_relationship()
    
    # 3. Suggérer le redémarrage
    restart_berinia_server()
    
    print(f"\n✅ Toutes les corrections possibles ont été appliquées.")
    return True

if __name__ == "__main__":
    main()
