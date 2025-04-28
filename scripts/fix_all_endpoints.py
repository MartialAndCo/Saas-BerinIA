#!/usr/bin/env python3
"""
Script pour corriger tous les problèmes de sérialisation des leads dans les API routes de Berinia.
Ce script cible spécifiquement les endpoints campaigns et niches qui génèrent encore des erreurs.
"""

import os
import sys
import re
import logging
from datetime import datetime
import json

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-api-fix")

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
    
    if not os.path.exists(BERINIA_SCHEMAS_DIR):
        print(f"❌ Répertoire des schémas introuvable: {BERINIA_SCHEMAS_DIR}")
        return False
    
    return True

def find_specific_files():
    """Trouver les fichiers spécifiques à corriger"""
    endpoints_to_fix = {}
    
    # Chercher les fichiers relatifs aux campagnes et niches
    for filename in os.listdir(API_ENDPOINTS_DIR):
        if filename.endswith('.py'):
            if "campaign" in filename or "niche" in filename:
                filepath = os.path.join(API_ENDPOINTS_DIR, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                    # Vérifier s'il y a des relations avec les leads
                    if "lead" in content.lower() and "response_model" in content:
                        endpoints_to_fix[filepath] = content
    
    return endpoints_to_fix

def fix_response_model_types(files_content):
    """Corriger les types de response_model pour utiliser des IDs au lieu d'objets Lead"""
    modifications = []
    
    for filepath, content in files_content.items():
        filename = os.path.basename(filepath)
        
        # Sauvegarde du contenu original
        backup_path = f"{filepath}.bak"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
                print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Chercher les déclarations de response_model qui contiennent Lead
        pattern = r'(@router\.[a-z]+\(.*response_model\s*=\s*[^,\)]+)'
        matches = re.findall(pattern, content)
        
        modified_content = content
        for match in matches:
            if "Lead" in match:
                new_match = match.replace("List[Lead]", "List[int]")
                modified_content = modified_content.replace(match, new_match)
                modifications.append(f"Correction du type de response_model dans {filename}")
        
        # Enregistrer les modifications si nécessaire
        if modified_content != content:
            with open(filepath, 'w') as f:
                f.write(modified_content)
                print(f"✅ Types de response_model corrigés dans {filename}")
    
    return modifications

def find_and_fix_campaign_endpoint():
    """Trouver et corriger spécifiquement l'endpoint des campagnes"""
    campaign_endpoint = os.path.join(API_ENDPOINTS_DIR, "campaigns.py")
    niche_endpoint = os.path.join(API_ENDPOINTS_DIR, "niches.py")
    
    endpoints_fixed = []
    
    # Correction de l'endpoint campaigns.py
    if os.path.exists(campaign_endpoint):
        print(f"\n🔍 Analyse et correction de l'endpoint campagnes...")
        
        with open(campaign_endpoint, 'r') as f:
            content = f.read()
            
        # Sauvegarde du contenu original
        backup_path = f"{campaign_endpoint}.bak2"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
                print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Rechercher les fonctions qui retournent des campagnes
        functions = []
        lines = content.split('\n')
        current_function = []
        in_function = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith("def ") and ("get_" in line.lower() or "read_" in line.lower()):
                if current_function:
                    functions.append(current_function)
                current_function = [i]
                in_function = True
            elif in_function:
                if line.strip().startswith("def ") or (not line.strip() and i < len(lines)-1 and lines[i+1].strip().startswith("def ")):
                    functions.append(current_function)
                    current_function = []
                    in_function = False
                else:
                    current_function.append(i)
        
        if current_function:
            functions.append(current_function)
        
        # Analyser et modifier les fonctions
        modified_lines = lines.copy()
        fix_made = False
        
        for function in functions:
            function_text = '\n'.join([lines[i] for i in function])
            function_name = re.search(r'def\s+([a-zA-Z0-9_]+)', lines[function[0]]).group(1)
            
            # Vérifier si la fonction retourne des campagnes avec des leads
            if "return" in function_text and "lead" in function_text.lower():
                print(f"🔧 Correction de la fonction {function_name} dans campaigns.py")
                
                # Insérer le code qui transforme les leads en IDs avant le return
                for i, line_idx in enumerate(function):
                    line = lines[line_idx]
                    
                    # Chercher les lignes de return
                    if "return" in line and not "return_" in line:
                        indent = len(line) - len(line.lstrip())
                        spaces = ' ' * indent
                        
                        # Préparation du code pour convertir les leads en IDs
                        lead_transform_code = [
                            f"{spaces}# Conversion des leads en IDs pour éviter l'erreur de sérialisation",
                            f"{spaces}for campaign in db_campaigns:",
                            f"{spaces}    if hasattr(campaign, 'leads') and campaign.leads:",
                            f"{spaces}        # Convertir tous les objets Lead en leurs IDs",
                            f"{spaces}        campaign.leads = [lead.id for lead in campaign.leads]"
                        ]
                        
                        # Insérer le code de transformation avant le return
                        for j, transform_line in enumerate(lead_transform_code):
                            modified_lines.insert(line_idx + j, transform_line)
                        
                        # Ajuster les indices des lignes suivantes
                        for k in range(i+1, len(function)):
                            function[k] += len(lead_transform_code)
                        
                        fix_made = True
                        break
        
        # Enregistrer les modifications si nécessaire
        if fix_made:
            with open(campaign_endpoint, 'w') as f:
                f.write('\n'.join(modified_lines))
            
            print(f"✅ Endpoint campaigns.py corrigé avec succès")
            endpoints_fixed.append("campaigns.py")
    
    # Correction de l'endpoint niches.py
    if os.path.exists(niche_endpoint):
        print(f"\n🔍 Analyse et correction de l'endpoint niches...")
        
        with open(niche_endpoint, 'r') as f:
            content = f.read()
            
        # Sauvegarde du contenu original
        backup_path = f"{niche_endpoint}.bak2"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
                print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Rechercher les fonctions qui retournent des niches
        functions = []
        lines = content.split('\n')
        current_function = []
        in_function = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith("def ") and ("get_" in line.lower() or "read_" in line.lower()):
                if current_function:
                    functions.append(current_function)
                current_function = [i]
                in_function = True
            elif in_function:
                if line.strip().startswith("def ") or (not line.strip() and i < len(lines)-1 and lines[i+1].strip().startswith("def ")):
                    functions.append(current_function)
                    current_function = []
                    in_function = False
                else:
                    current_function.append(i)
        
        if current_function:
            functions.append(current_function)
        
        # Analyser et modifier les fonctions
        modified_lines = lines.copy()
        fix_made = False
        
        for function in functions:
            function_text = '\n'.join([lines[i] for i in function])
            function_name = re.search(r'def\s+([a-zA-Z0-9_]+)', lines[function[0]]).group(1)
            
            # Vérifier si la fonction retourne des niches avec des campagnes qui ont des leads
            if "return" in function_text and "campagne" in function_text.lower():
                print(f"🔧 Correction de la fonction {function_name} dans niches.py")
                
                # Insérer le code qui transforme les leads en IDs avant le return
                for i, line_idx in enumerate(function):
                    line = lines[line_idx]
                    
                    # Chercher les lignes de return
                    if "return" in line and not "return_" in line:
                        indent = len(line) - len(line.lstrip())
                        spaces = ' ' * indent
                        
                        # Préparation du code pour convertir les leads en IDs
                        lead_transform_code = [
                            f"{spaces}# Conversion des leads en IDs pour éviter l'erreur de sérialisation",
                            f"{spaces}for niche in db_niches:",
                            f"{spaces}    if hasattr(niche, 'campagnes'):  # Vérifier si la niche a des campagnes",
                            f"{spaces}        for campagne in niche.campagnes:  # Pour chaque campagne",
                            f"{spaces}            if hasattr(campagne, 'leads') and campagne.leads:  # Si la campagne a des leads",
                            f"{spaces}                # Convertir les objets Lead en leurs IDs",
                            f"{spaces}                campagne.leads = [lead.id for lead in campagne.leads]"
                        ]
                        
                        # Insérer le code de transformation avant le return
                        for j, transform_line in enumerate(lead_transform_code):
                            modified_lines.insert(line_idx + j, transform_line)
                        
                        # Ajuster les indices des lignes suivantes
                        for k in range(i+1, len(function)):
                            function[k] += len(lead_transform_code)
                        
                        fix_made = True
                        break
        
        # Enregistrer les modifications si nécessaire
        if fix_made:
            with open(niche_endpoint, 'w') as f:
                f.write('\n'.join(modified_lines))
            
            print(f"✅ Endpoint niches.py corrigé avec succès")
            endpoints_fixed.append("niches.py")
    
    return endpoints_fixed

def create_schema_conversion():
    """Créer ou mettre à jour les schémas pour assurer la conversion des leads en IDs"""
    schema_fixes = []
    
    # Chercher le schéma de campagne
    campaign_schema = os.path.join(BERINIA_SCHEMAS_DIR, "campaign.py")
    if os.path.exists(campaign_schema):
        print(f"\n🔍 Analyse et mise à jour du schéma de campagne...")
        
        with open(campaign_schema, 'r') as f:
            content = f.read()
        
        # Sauvegarde du contenu original
        backup_path = f"{campaign_schema}.bak"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
                print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Chercher les définitions de classe qui contiennent le champ leads
        leads_field_pattern = r'(\s+leads\s*:.+)'
        matches = re.findall(leads_field_pattern, content)
        
        modified_content = content
        for match in matches:
            if "List[Lead]" in match:
                new_match = match.replace("List[Lead]", "List[int]")
                modified_content = modified_content.replace(match, new_match)
                schema_fixes.append("Correction du type leads dans le schéma Campaign")
        
        # Enregistrer les modifications si nécessaire
        if modified_content != content:
            with open(campaign_schema, 'w') as f:
                f.write(modified_content)
                print(f"✅ Type du champ leads corrigé dans le schéma Campaign")
    
    # Vérifier le schéma de niche (qui pourrait contenir des campagnes avec des leads)
    niche_schema = os.path.join(BERINIA_SCHEMAS_DIR, "niche.py")
    if os.path.exists(niche_schema):
        print(f"\n🔍 Analyse et mise à jour du schéma de niche...")
        
        with open(niche_schema, 'r') as f:
            content = f.read()
        
        # Sauvegarde du contenu original
        backup_path = f"{niche_schema}.bak"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
                print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Vérifier s'il y a des références aux objets Lead dans les campagnes
        if "Lead" in content and "campagnes" in content:
            # Chercher les relations avec les leads dans les campagnes
            campaign_class_pattern = r'(class\s+Campaign.+?^(?=\S))'
            campaign_class_matches = re.findall(campaign_class_pattern, content, re.DOTALL | re.MULTILINE)
            
            if campaign_class_matches:
                modified_content = content
                for campaign_class in campaign_class_matches:
                    leads_field_pattern = r'(\s+leads\s*:.+)'
                    leads_matches = re.findall(leads_field_pattern, campaign_class)
                    
                    if leads_matches:
                        for match in leads_matches:
                            if "List[Lead]" in match:
                                new_match = match.replace("List[Lead]", "List[int]")
                                modified_content = modified_content.replace(match, new_match)
                                schema_fixes.append("Correction du type leads dans le schéma Campaign à l'intérieur de Niche")
                
                # Enregistrer les modifications si nécessaire
                if modified_content != content:
                    with open(niche_schema, 'w') as f:
                        f.write(modified_content)
                        print(f"✅ Type du champ leads corrigé dans le schéma Campaign à l'intérieur de Niche")
    
    return schema_fixes

def main():
    print(f"\n{'='*50}")
    print(f"🔧 CORRECTION COMPLÈTE DES PROBLÈMES DE SÉRIALISATION DES LEADS")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    if not check_paths():
        print("❌ Vérification des chemins échouée. Veuillez vérifier les chemins d'accès.")
        return False
    
    # Étape 1: Analyser et corriger les schémas
    print("\n📊 ÉTAPE 1: CORRECTION DES SCHÉMAS")
    schema_fixes = create_schema_conversion()
    
    # Étape 2: Corriger les response_model dans les endpoints
    print("\n🔌 ÉTAPE 2: CORRECTION DES TYPES DE RESPONSE_MODEL")
    files_content = find_specific_files()
    response_model_fixes = fix_response_model_types(files_content)
    
    # Étape 3: Corriger les endpoints de campagnes et niches
    print("\n🔧 ÉTAPE 3: CORRECTION DES ENDPOINTS SPÉCIFIQUES")
    endpoints_fixed = find_and_fix_campaign_endpoint()
    
    # Rapport des corrections effectuées
    print(f"\n{'='*50}")
    print(f"📋 RÉSUMÉ DES CORRECTIONS EFFECTUÉES")
    print(f"{'='*50}")
    
    if schema_fixes:
        print("\n✅ Schémas corrigés:")
        for fix in schema_fixes:
            print(f"  - {fix}")
    else:
        print("\n⚠️ Aucune correction nécessaire dans les schémas")
    
    if response_model_fixes:
        print("\n✅ Types de response_model corrigés:")
        for fix in response_model_fixes:
            print(f"  - {fix}")
    else:
        print("\n⚠️ Aucune correction nécessaire dans les types de response_model")
    
    if endpoints_fixed:
        print("\n✅ Endpoints spécifiques corrigés:")
        for endpoint in endpoints_fixed:
            print(f"  - {endpoint}")
    else:
        print("\n⚠️ Aucun endpoint spécifique corrigé")
    
    # Étape 4: Redémarrer l'API (à adapter selon le processus de démarrage de Berinia)
    print(f"\n{'='*50}")
    print(f"🚀 INSTRUCTIONS DE REDÉMARRAGE")
    print(f"{'='*50}")
    print("Pour appliquer les corrections, veuillez:")
    print("1. Redémarrer le serveur Berinia (si un script de démarrage est disponible)")
    print("2. Redémarrer le système infra-ia:")
    print("   python3 start_brain_agent.py")
    
    return True

if __name__ == "__main__":
    main()
