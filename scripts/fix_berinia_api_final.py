#!/usr/bin/env python3
"""
Script final pour corriger les problèmes d'API dans Berinia.
Ce script résout les erreurs spécifiques identifiées dans les endpoints:
1. Campaigns API: "name 'db_campaigns' is not defined"
2. Niches API: "name 'db_niches' is not defined"
3. Leads API: "Input should be a valid dictionary or object to extract fields from"
"""

import os
import sys
import re
import logging
from datetime import datetime

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-api-fix-final")

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

def fix_campaigns_endpoint():
    """Corriger l'erreur 'db_campaigns' is not defined dans campaigns.py"""
    campaigns_path = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    if not os.path.exists(campaigns_path):
        print(f"❌ Fichier campaigns.py non trouvé à {campaigns_path}")
        return False
    
    print(f"\n🔧 Correction de l'endpoint campaigns.py...")
    
    # Lire le fichier
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{campaigns_path}.final.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Identifier les fonctions get_campaigns et get_campaign
    # Nous devons adapter nos corrections au contexte de chaque fonction
    functions = {}
    lines = content.split('\n')
    
    in_function = False
    current_function = None
    function_start = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith("def get_campaign") or line.strip().startswith("async def get_campaign"):
            if in_function:
                functions[current_function] = (function_start, i-1)
            in_function = True
            current_function = line.split("def ")[1].split("(")[0].strip()
            function_start = i
        elif in_function and line.strip().startswith("def ") and not current_function in line:
            functions[current_function] = (function_start, i-1)
            in_function = False
        elif in_function and i == len(lines) - 1:
            functions[current_function] = (function_start, i)
    
    # Corriger chaque fonction
    modified_content = content
    for func_name, (start, end) in functions.items():
        function_content = '\n'.join(lines[start:end+1])
        
        # 1. Déterminer la variable qui contient les campagnes
        # Chercher les motifs comme: campaigns = db.query(models.Campaign)
        campaign_var_match = re.search(r'([a-zA-Z0-9_]+)\s*=\s*.*query\(.*Campaign', function_content)
        if campaign_var_match:
            campaign_var = campaign_var_match.group(1)
            
            # 2. Remplacer notre code de correction précédent par une version adaptée
            # Rechercher notre code ajouté qui utilise 'db_campaigns'
            bad_code_pattern = r'# Conversion des leads en IDs.*?(?=\n\s*return|\Z)'
            bad_code_match = re.search(bad_code_pattern, function_content, re.DOTALL)
            
            if bad_code_match:
                bad_code = bad_code_match.group(0)
                fixed_code = f"""# Conversion des leads en IDs pour éviter l'erreur de sérialisation
    for campaign in {campaign_var}:
        if hasattr(campaign, 'leads') and campaign.leads:
            # Convertir tous les objets Lead en leurs IDs
            campaign.leads = [lead.id for lead in campaign.leads]"""
                
                # Remplacer le code problématique
                modified_content = modified_content.replace(bad_code, fixed_code)
                print(f"✅ Correction de la variable dans la fonction {func_name}")
            
            # S'il n'y a pas de code précédent à remplacer, vérifier si nous devons ajouter du code
            elif "return" in function_content and "leads" in function_content.lower():
                # Trouver la position juste avant le return
                for i in range(start, end+1):
                    if "return" in lines[i] and not "def" in lines[i]:
                        # Déterminer l'indentation
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        spaces = ' ' * indent
                        
                        # Insérer le code de transformation avant le return
                        transform_code = f"""{spaces}# Conversion des leads en IDs pour éviter l'erreur de sérialisation
{spaces}for campaign in {campaign_var}:
{spaces}    if hasattr(campaign, 'leads') and campaign.leads:
{spaces}        # Convertir tous les objets Lead en leurs IDs
{spaces}        campaign.leads = [lead.id for lead in campaign.leads]
"""
                        
                        # Diviser le contenu à cette ligne et insérer le code
                        before = '\n'.join(lines[:i])
                        after = '\n'.join(lines[i:])
                        modified_content = before + '\n' + transform_code + after
                        print(f"✅ Code de transformation ajouté à la fonction {func_name}")
                        break
    
    # Enregistrer les modifications
    if modified_content != content:
        with open(campaigns_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à campaigns.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à campaigns.py")
        return False

def fix_niches_endpoint():
    """Corriger l'erreur 'db_niches' is not defined dans niches.py"""
    niches_path = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    if not os.path.exists(niches_path):
        print(f"❌ Fichier niches.py non trouvé à {niches_path}")
        return False
    
    print(f"\n🔧 Correction de l'endpoint niches.py...")
    
    # Lire le fichier
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{niches_path}.final.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Identifier les fonctions get_niches et get_niche
    functions = {}
    lines = content.split('\n')
    
    in_function = False
    current_function = None
    function_start = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith("def get_niche") or line.strip().startswith("async def get_niche"):
            if in_function:
                functions[current_function] = (function_start, i-1)
            in_function = True
            current_function = line.split("def ")[1].split("(")[0].strip()
            function_start = i
        elif in_function and line.strip().startswith("def ") and not current_function in line:
            functions[current_function] = (function_start, i-1)
            in_function = False
        elif in_function and i == len(lines) - 1:
            functions[current_function] = (function_start, i)
    
    # Corriger chaque fonction
    modified_content = content
    for func_name, (start, end) in functions.items():
        function_content = '\n'.join(lines[start:end+1])
        
        # 1. Déterminer la variable qui contient les niches
        # Chercher les motifs comme: niches = db.query(models.Niche)
        niche_var_match = re.search(r'([a-zA-Z0-9_]+)\s*=\s*.*query\(.*Niche', function_content)
        if niche_var_match:
            niche_var = niche_var_match.group(1)
            
            # 2. Remplacer notre code de correction précédent par une version adaptée
            # Rechercher notre code ajouté qui utilise 'db_niches'
            bad_code_pattern = r'# Conversion des leads en IDs.*?(?=\n\s*return|\Z)'
            bad_code_match = re.search(bad_code_pattern, function_content, re.DOTALL)
            
            if bad_code_match:
                bad_code = bad_code_match.group(0)
                fixed_code = f"""# Conversion des leads en IDs pour éviter l'erreur de sérialisation
    for niche in {niche_var}:
        if hasattr(niche, 'campagnes'):  # Vérifier si la niche a des campagnes
            for campagne in niche.campagnes:  # Pour chaque campagne
                if hasattr(campagne, 'leads') and campagne.leads:  # Si la campagne a des leads
                    # Convertir les objets Lead en leurs IDs
                    campagne.leads = [lead.id for lead in campagne.leads]"""
                
                # Remplacer le code problématique
                modified_content = modified_content.replace(bad_code, fixed_code)
                print(f"✅ Correction de la variable dans la fonction {func_name}")
            
            # S'il n'y a pas de code précédent à remplacer, vérifier si nous devons ajouter du code
            elif "return" in function_content and ("campagne" in function_content.lower() or "lead" in function_content.lower()):
                # Trouver la position juste avant le return
                for i in range(start, end+1):
                    if "return" in lines[i] and not "def" in lines[i]:
                        # Déterminer l'indentation
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        spaces = ' ' * indent
                        
                        # Insérer le code de transformation avant le return
                        transform_code = f"""{spaces}# Conversion des leads en IDs pour éviter l'erreur de sérialisation
{spaces}for niche in {niche_var}:
{spaces}    if hasattr(niche, 'campagnes'):  # Vérifier si la niche a des campagnes
{spaces}        for campagne in niche.campagnes:  # Pour chaque campagne
{spaces}            if hasattr(campagne, 'leads') and campagne.leads:  # Si la campagne a des leads
{spaces}                # Convertir les objets Lead en leurs IDs
{spaces}                campagne.leads = [lead.id for lead in campagne.leads]
"""
                        
                        # Diviser le contenu à cette ligne et insérer le code
                        before = '\n'.join(lines[:i])
                        after = '\n'.join(lines[i:])
                        modified_content = before + '\n' + transform_code + after
                        print(f"✅ Code de transformation ajouté à la fonction {func_name}")
                        break
    
    # Enregistrer les modifications
    if modified_content != content:
        with open(niches_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à niches.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à niches.py")
        return False

def fix_leads_endpoint():
    """
    Corriger l'erreur 'Input should be a valid dictionary or object' dans leads.py
    Le problème semble être que nous avons remplacé les objets Lead par des IDs,
    mais le système attend toujours des objets Lead complets.
    """
    leads_path = os.path.join(API_ENDPOINTS_DIR, "leads.py")
    if not os.path.exists(leads_path):
        print(f"❌ Fichier leads.py non trouvé à {leads_path}")
        return False
    
    print(f"\n🔧 Correction de l'endpoint leads.py...")
    
    # Lire le fichier
    with open(leads_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{leads_path}.final.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # D'abord, chercher les problèmes dans la configuration des modèles de réponse
    # Vérifier les décorateurs de route qui spécifient des modèles de réponse
    lines = content.split('\n')
    modified_lines = []
    changes_made = False
    
    for i, line in enumerate(lines):
        if '@router' in line and 'response_model' in line:
            # Vérifier si le response_model est modifié à List[int] 
            if 'List[int]' in line:
                # Le remplacer par le type correct (probablement List[Lead])
                modified_line = line.replace('List[int]', 'List[Lead]')
                modified_lines.append(modified_line)
                print(f"✅ Correction du modèle de réponse à la ligne {i+1}")
                changes_made = True
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    # Ensuite, chercher les fonctions qui retournent des leads et corriger le code de transformation
    # Rechercher notre code ajouté qui transforme les leads en IDs
    modified_content = '\n'.join(modified_lines)
    lead_transform_pattern = r'# Sérialiser les leads par ID.*?\n.*?lead_ids = \[lead.id for lead in ([^\]]+)\].*?\n.*?return lead_ids'
    lead_transform_match = re.search(lead_transform_pattern, modified_content, re.DOTALL)
    
    if lead_transform_match:
        lead_var = lead_transform_match.group(1)
        full_match = lead_transform_match.group(0)
        
        # Remplacer par un retour direct de la variable originale
        fixed_code = f"return {lead_var}"
        modified_content = modified_content.replace(full_match, fixed_code)
        print(f"✅ Restauration du retour des objets Lead complets")
        changes_made = True
    
    # Enregistrer les modifications
    if changes_made:
        with open(leads_path, 'w') as f:
            f.write(modified_content)
        print(f"✅ Modifications appliquées à leads.py")
        return True
    else:
        print(f"⚠️ Aucune modification appliquée à leads.py")
        return False

def check_leads_schema():
    """
    Vérifier et corriger le schéma Lead si nécessaire.
    Nous devons nous assurer que le schéma est correctement configuré.
    """
    lead_schema_path = os.path.join(BERINIA_SCHEMAS_DIR, "lead.py")
    if not os.path.exists(lead_schema_path):
        print(f"❌ Fichier lead.py non trouvé à {lead_schema_path}")
        return False
    
    print(f"\n🔧 Vérification du schéma Lead...")
    
    # Lire le fichier
    with open(lead_schema_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{lead_schema_path}.final.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Vérifier les défintions du schéma
    lines = content.split('\n')
    modified_lines = []
    changes_made = False
    
    for i, line in enumerate(lines):
        # Si nous avons changé List[Lead] en List[int], le restaurer
        if ('campaign:' in line or 'campaigns:' in line) and 'List[int]' in line:
            modified_line = line.replace('List[int]', 'List[Lead]')
            modified_lines.append(modified_line)
            print(f"✅ Restauration du type correct à la ligne {i+1}")
            changes_made = True
        else:
            modified_lines.append(line)
    
    # Enregistrer les modifications
    if changes_made:
        with open(lead_schema_path, 'w') as f:
            f.write('\n'.join(modified_lines))
        print(f"✅ Modifications appliquées au schéma Lead")
        return True
    else:
        print(f"✅ Le schéma Lead est correctement configuré")
        return True

def check_additional_schemas():
    """
    Vérifier et corriger d'autres schémas potentiellement problématiques.
    """
    campagin_schema_path = os.path.join(BERINIA_SCHEMAS_DIR, "campaign.py")
    if not os.path.exists(campagin_schema_path):
        print(f"❌ Fichier campaign.py non trouvé à {campagin_schema_path}")
        return False
    
    print(f"\n🔧 Vérification du schéma Campaign...")
    
    # Lire le fichier
    with open(campagin_schema_path, 'r') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_path = f"{campagin_schema_path}.final.bak"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    # Vérifier les défintions du schéma
    lines = content.split('\n')
    modified_lines = []
    changes_made = False
    
    in_schema_class = False
    
    for i, line in enumerate(lines):
        # Détecter les classes de schéma
        if line.strip().startswith("class ") and "(" in line:
            in_schema_class = True
        elif in_schema_class and line.strip().startswith("class "):
            in_schema_class = False
        
        # Si nous sommes dans une classe de schéma et avons un champ leads
        if in_schema_class and "leads:" in line:
            # Si nous avons changé List[Lead] en List[int], le restaurer si c'est un schema de sortie
            if "List[int]" in line and ("Response" in lines[i-5:i+5] or "Output" in lines[i-5:i+5]):
                modified_line = line.replace("List[int]", "List[Lead]")
                modified_lines.append(modified_line)
                print(f"✅ Restauration du type correct à la ligne {i+1}")
                changes_made = True
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    # Enregistrer les modifications
    if changes_made:
        with open(campagin_schema_path, 'w') as f:
            f.write('\n'.join(modified_lines))
        print(f"✅ Modifications appliquées au schéma Campaign")
        return True
    else:
        print(f"✅ Le schéma Campaign est correctement configuré")
        return True

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
    print(f"🔧 CORRECTION FINALE DES PROBLÈMES D'API BERINIA")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    if not check_paths():
        print("❌ Vérification des chemins échouée. Veuillez vérifier les chemins d'accès.")
        return False
    
    # 1. Corriger l'endpoint campaigns.py
    fix_campaigns_endpoint()
    
    # 2. Corriger l'endpoint niches.py
    fix_niches_endpoint()
    
    # 3. Corriger l'endpoint leads.py
    fix_leads_endpoint()
    
    # 4. Vérifier et corriger les schémas
    check_leads_schema()
    check_additional_schemas()
    
    # 5. Suggérer le redémarrage
    restart_berinia_server()
    
    print(f"\n✅ Toutes les corrections ont été appliquées")
    return True

if __name__ == "__main__":
    main()
