#!/usr/bin/env python3
"""
Script pour corriger le problème de sérialisation des leads dans les API routes de Berinia.
L'erreur indique que la réponse contient directement des objets Lead au lieu d'entiers.
"""

import os
import sys
import logging
from datetime import datetime
import inspect
import importlib.util
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-api-fix")

# Chemins vers les fichiers Berinia
BERINIA_BACKEND_PATH = os.getenv("BERINIA_BACKEND_PATH", "/root/berinia/backend")
API_ROUTES_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "api", "endpoints")
BERINIA_API_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "api")
BERINIA_SCHEMAS_DIR = os.path.join(BERINIA_BACKEND_PATH, "app", "schemas")

def is_berinia_available():
    """Vérifie si les répertoires de Berinia sont accessibles"""
    if not os.path.exists(BERINIA_BACKEND_PATH):
        logger.error(f"❌ Chemin backend Berinia introuvable: {BERINIA_BACKEND_PATH}")
        return False
    if not os.path.exists(API_ROUTES_DIR):
        logger.error(f"❌ Répertoire des routes API introuvable: {API_ROUTES_DIR}")
        return False
    return True

def find_lead_related_files():
    """
    Recherche les fichiers liés aux leads et à la sérialisation dans le backend Berinia
    """
    lead_files = []
    
    # Chercher dans les routes API
    for root, dirs, files in os.walk(API_ROUTES_DIR):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'lead' in content.lower() or 'Lead' in content:
                        lead_files.append(filepath)
    
    # Chercher les schémas de leads
    for root, dirs, files in os.walk(BERINIA_SCHEMAS_DIR):
        for file in files:
            if file.endswith(".py") and ('lead' in file.lower() or 'response' in file.lower()):
                filepath = os.path.join(root, file)
                lead_files.append(filepath)
    
    return lead_files

def inspect_file_content(filepath):
    """
    Analyse le contenu d'un fichier pour comprendre comment les leads sont traités
    """
    print(f"\n📄 Analyse de {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Rechercher des patterns spécifiques liés à la sérialisation des leads
    patterns = {
        "route_def": ["@router.get", "@router.post", "@app.get", "@app.post"],
        "lead_model": ["Lead(", "List[Lead]", "LeadCreate", "LeadResponse"],
        "response_model": ["response_model=", "ResponseModel"],
        "serialize": ["jsonable_encoder", "model_dump", "to_dict", "serialize"]
    }
    
    findings = {}
    for category, search_terms in patterns.items():
        lines = []
        for term in search_terms:
            for i, line in enumerate(content.split('\n')):
                if term in line:
                    lines.append((i+1, line.strip()))
        if lines:
            findings[category] = lines
    
    # Afficher les résultats
    if findings:
        for category, lines in findings.items():
            print(f"  🔍 {category.upper()}:")
            for line_num, line in lines:
                print(f"    Ligne {line_num}: {line}")
    else:
        print("  ⚠️ Aucun pattern pertinent trouvé")
    
    return findings

def fix_response_model(filepath):
    """
    Corrige les problèmes de sérialisation dans les fichiers de réponse
    """
    # Lire le fichier
    with open(filepath, 'r') as f:
        content = f.read()
        original_content = content
    
    # Identifier les patterns de problèmes courants
    fixes_made = []
    
    # Cas 1: Direct inclusion of Lead objects in response
    if "response: List[Lead]" in content or "response: List[models.Lead]" in content:
        content = content.replace("response: List[Lead]", "response: List[int]")
        content = content.replace("response: List[models.Lead]", "response: List[int]")
        fixes_made.append("Correction du typage des listes de leads (List[Lead] -> List[int])")
    
    # Cas 2: Returning Lead objects directly
    lead_return_patterns = [
        "return leads",
        "return db_leads",
        "return [lead for lead",
        "return await leads",
        "return {"
    ]
    
    for pattern in lead_return_patterns:
        if pattern in content:
            # Analyse plus détaillée requise
            lines = content.split('\n')
            modified_lines = []
            
            for i, line in enumerate(lines):
                if pattern in line and ("lead" in line.lower() or "campaign" in line.lower()):
                    # Vérifier s'il faut ajouter un code de sérialisation
                    context_lines = lines[max(0, i-5):i] + [line] + lines[i+1:min(len(lines), i+5)]
                    context = '\n'.join(context_lines)
                    
                    # Si on retourne directement une liste d'objets sans sérialisation
                    if (pattern == "return leads" or pattern == "return db_leads") and "jsonable_encoder" not in context and "model_dump" not in context:
                        indent = len(line) - len(line.lstrip())
                        spaces = ' ' * indent
                        
                        # Ajouter une fonction de sérialisation
                        if "return [" in line:
                            serialized_line = line.replace("return [", f"return [{spaces}lead.id for ")
                            modified_lines.append(serialized_line)
                            fixes_made.append(f"Ajout de sérialisation par ID à la ligne {i+1}")
                        else:
                            modified_lines.append(f"{spaces}# Sérialiser les leads par ID")
                            modified_lines.append(f"{spaces}lead_ids = [lead.id for lead in {pattern.replace('return ', '')}]")
                            modified_lines.append(f"{spaces}return lead_ids")
                            fixes_made.append(f"Remplacement de la réponse par des IDs de lead à la ligne {i+1}")
                        continue
                    
                    # Si on retourne un dict avec des objets leads
                    elif pattern == "return {" and ("'leads'" in context or '"leads"' in context):
                        # On va devoir analyser et modifier cette section plus en détail
                        in_response_block = False
                        response_block_lines = []
                        
                        for j in range(i, min(len(lines), i+20)):
                            line_j = lines[j]
                            if pattern in line_j and not in_response_block:
                                in_response_block = True
                                response_block_lines.append(line_j)
                            elif in_response_block:
                                if "}" in line_j and line_j.strip() == "}":
                                    # Fin du bloc de réponse
                                    response_block_lines.append(line_j)
                                    break
                                elif "'leads'" in line_j or '"leads"' in line_j:
                                    # Ligne avec la clé 'leads', à modifier
                                    if ":" in line_j:
                                        key_part = line_j.split(":")[0]
                                        indent = len(line_j) - len(line_j.lstrip())
                                        spaces = ' ' * indent
                                        # Remplacer par une liste d'IDs
                                        response_block_lines.append(f"{spaces}{key_part}: [lead.id for lead in leads],")
                                        fixes_made.append(f"Conversion des objets leads en liste d'IDs à la ligne {j+1}")
                                    else:
                                        response_block_lines.append(line_j)
                                else:
                                    response_block_lines.append(line_j)
                        
                        if response_block_lines:
                            # Remplacer le bloc original par notre version corrigée
                            response_block = '\n'.join(response_block_lines)
                            start_line = i
                            end_line = i + len(response_block_lines)
                            
                            # Ajouter les lignes avant ce bloc
                            modified_lines.extend(lines[:start_line])
                            # Ajouter notre bloc corrigé
                            modified_lines.append(response_block)
                            # On va sauter à la fin du bloc
                            i = end_line - 1
                            continue
                
                # Ligne sans modification
                modified_lines.append(line)
            
            # Mettre à jour le contenu si des modifications ont été apportées
            if modified_lines:
                content = '\n'.join(modified_lines)
    
    # Enregistrer les modifications si des corrections ont été apportées
    if fixes_made and content != original_content:
        backup_path = f"{filepath}.bak"
        os.rename(filepath, backup_path)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"\n✅ Corrections apportées au fichier {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}:")
        for fix in fixes_made:
            print(f"  - {fix}")
        print(f"📋 Sauvegarde du fichier original: {os.path.relpath(backup_path, BERINIA_BACKEND_PATH)}")
        return True
    else:
        print(f"\n⚠️ Aucune correction nécessaire dans {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
        return False

def fix_schema_model(filepath):
    """
    Corrige les définitions de schémas Pydantic pour les réponses contenant des leads
    """
    # Lire le fichier
    with open(filepath, 'r') as f:
        content = f.read()
        original_content = content
    
    # Identifier les schémas de réponse qui pourraient retourner des objets Lead directement
    schema_fixes = []
    lines = content.split('\n')
    modified_lines = []
    
    in_response_class = False
    current_class_name = ""
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Trouver les définitions de classe
        if line.strip().startswith("class ") and "Response" in line and "(" in line:
            class_def = line.strip()
            current_class_name = class_def.split("class ")[1].split("(")[0].strip()
            in_response_class = True
            modified_lines.append(line)
        
        # Analyser l'intérieur des classes de réponse
        elif in_response_class:
            if line.strip().startswith("class ") or not line.strip():
                # Fin de la classe courante
                in_response_class = False
                current_class_name = ""
                modified_lines.append(line)
            elif "leads:" in line or "lead:" in line:
                # Analyser la définition du champ leads
                if ("List[Lead]" in line or "List[models.Lead]" in line or 
                    "Lead " in line or "models.Lead" in line):
                    # Corriger pour utiliser des IDs à la place
                    indent = len(line) - len(line.lstrip())
                    spaces = ' ' * indent
                    
                    if "List[" in line:
                        corrected_line = line.replace("List[Lead]", "List[int]")
                        corrected_line = corrected_line.replace("List[models.Lead]", "List[int]")
                        schema_fixes.append(f"Correction du typage List[Lead] en List[int] dans {current_class_name}")
                    else:
                        corrected_line = line.replace("Lead ", "int ")
                        corrected_line = corrected_line.replace("models.Lead", "int")
                        schema_fixes.append(f"Correction du typage Lead en int dans {current_class_name}")
                    
                    modified_lines.append(corrected_line)
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
        
        i += 1
    
    # Enregistrer les modifications si des corrections ont été apportées
    content = '\n'.join(modified_lines)
    if schema_fixes and content != original_content:
        backup_path = f"{filepath}.bak"
        os.rename(filepath, backup_path)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"\n✅ Corrections apportées au schéma {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}:")
        for fix in schema_fixes:
            print(f"  - {fix}")
        print(f"📋 Sauvegarde du fichier original: {os.path.relpath(backup_path, BERINIA_BACKEND_PATH)}")
        return True
    else:
        print(f"\n⚠️ Aucune correction nécessaire dans le schéma {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
        return False

def clean_and_restart_api():
    """
    Redémarre l'API Berinia après avoir effectué les modifications
    """
    # Chemin du script de démarrage Berinia (à adapter)
    berinia_start_script = os.path.join(BERINIA_BACKEND_PATH, "start.sh")
    
    if os.path.exists(berinia_start_script):
        print("\n🔄 Redémarrage de l'API Berinia...")
        os.system(f"bash {berinia_start_script}")
        print("✅ API Berinia redémarrée")
    else:
        print("\n⚠️ Script de démarrage Berinia non trouvé")
        print(f"Pour redémarrer l'API, exécutez manuellement le script dans {BERINIA_BACKEND_PATH}")

def fix_api_leads_serialization():
    """
    Fonction principale pour corriger les problèmes de sérialisation des leads dans l'API
    """
    print(f"\n{'='*40}")
    print(f"🔧 CORRECTION DE LA SÉRIALISATION DES LEADS DANS L'API BERINIA")
    print(f"🕒 Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}\n")
    
    if not is_berinia_available():
        print("❌ Backend Berinia non disponible. Abandon.")
        return False
    
    print("🔍 Recherche des fichiers liés aux leads dans l'API...")
    lead_files = find_lead_related_files()
    
    if not lead_files:
        print("❌ Aucun fichier pertinent trouvé. Vérifiez les chemins d'accès.")
        return False
    
    print(f"✅ {len(lead_files)} fichiers identifiés pour analyse")
    
    # Phase 1: Analyse des fichiers
    print("\n📊 PHASE 1: ANALYSE DES FICHIERS")
    file_analysis = {}
    for filepath in lead_files:
        findings = inspect_file_content(filepath)
        file_analysis[filepath] = findings
    
    # Phase 2: Correction des fichiers concernés
    print("\n🔧 PHASE 2: CORRECTION DES FICHIERS")
    fixes_performed = 0
    
    # D'abord corriger les schémas
    schema_files = [f for f in lead_files if "/schemas/" in f]
    for filepath in schema_files:
        if fix_schema_model(filepath):
            fixes_performed += 1
    
    # Ensuite corriger les routes API
    api_files = [f for f in lead_files if "/api/" in f and "endpoints" in f]
    for filepath in api_files:
        if fix_response_model(filepath):
            fixes_performed += 1
    
    # Phase 3: Nettoyage et redémarrage
    if fixes_performed > 0:
        print(f"\n✅ {fixes_performed} fichiers corrigés")
        
        # Redémarrer l'API
        clean_and_restart_api()
        
        print("\n🚀 Pour tester les corrections dans le système infra-ia:")
        print("python3 start_brain_agent.py")
        return True
    else:
        print("\n⚠️ Aucune correction appliquée")
        print("Il est possible que les problèmes de sérialisation soient situés dans des emplacements non analysés.")
        print("Vérifiez manuellement le code des API endpoints et des schémas dans le backend Berinia.")
        return False

def examine_berinia_api_source():
    """Affiche des informations sur les chemins d'accès aux fichiers Berinia"""
    print(f"\n{'='*40}")
    print(f"📂 INFORMATIONS SUR LES CHEMINS D'ACCÈS AU BACKEND BERINIA")
    print(f"{'='*40}\n")
    
    print(f"Chemin backend Berinia: {BERINIA_BACKEND_PATH}")
    print(f"Répertoire API: {BERINIA_API_DIR}")
    print(f"Répertoire des routes API: {API_ROUTES_DIR}")
    print(f"Répertoire des schémas: {BERINIA_SCHEMAS_DIR}")
    
    # Vérifier l'existence des répertoires
    for path, name in [
        (BERINIA_BACKEND_PATH, "Backend Berinia"),
        (BERINIA_API_DIR, "API Berinia"),
        (API_ROUTES_DIR, "Routes API"),
        (BERINIA_SCHEMAS_DIR, "Schémas")
    ]:
        if os.path.exists(path):
            print(f"✅ {name} trouvé: {path}")
            
            # Lister quelques fichiers pour confirmation
            if os.path.isdir(path):
                files = os.listdir(path)
                print(f"   📄 Fichiers ({min(3, len(files))} sur {len(files)}):")
                for file in files[:3]:
                    print(f"      - {file}")
        else:
            print(f"❌ {name} introuvable: {path}")
    
    # Essayer de trouver des fichiers d'API endpoints spécifiques
    for root, dirs, files in os.walk(BERINIA_BACKEND_PATH):
        api_endpoints = [f for f in files if f.endswith(".py") and ("api" in root.lower() or "route" in root.lower())]
        if api_endpoints:
            print(f"\n📁 Endpoints API trouvés dans: {root}")
            print(f"   📄 Fichiers d'API ({min(5, len(api_endpoints))} sur {len(api_endpoints)}):")
            for file in api_endpoints[:5]:
                print(f"      - {file}")
            # Ne montrer que le premier dossier contenant des endpoints
            break

def find_and_fix_model_code():
    """
    Recherche et modifie les modèles et les routes qui gèrent la campagne et les leads
    """
    print(f"\n{'='*40}")
    print(f"🔍 RECHERCHE ET MODIFICATION DES MODÈLES ET ROUTES")
    print(f"{'='*40}\n")
    
    if not is_berinia_available():
        print("❌ Backend Berinia non disponible. Abandon.")
        return False
    
    # 1. Rechercher les fichiers contenant "campaign" et "lead" dans le dossier des modèles
    models_dir = os.path.join(BERINIA_BACKEND_PATH, "app", "models")
    if not os.path.exists(models_dir):
        print(f"❌ Répertoire des modèles introuvable: {models_dir}")
        return False
    
    campaigns_model_path = None
    leads_model_path = None
    
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    if "campaign" in content.lower() or "Campaign" in content:
                        campaigns_model_path = filepath
                        print(f"✅ Modèle de campagne trouvé: {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
                    if "lead" in content.lower() or "Lead" in content:
                        leads_model_path = filepath
                        print(f"✅ Modèle de lead trouvé: {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
    
    # 2. Analyser le modèle de campagne pour comprendre la relation avec les leads
    if campaigns_model_path:
        with open(campaigns_model_path, 'r') as f:
            content = f.read()
            print("\n📄 Analyse du modèle de campagne:")
            
            # Chercher les relations avec les leads
            relationship_lines = []
            for i, line in enumerate(content.split("\n")):
                if "relationship" in line.lower() and "lead" in line.lower():
                    relationship_lines.append((i+1, line.strip()))
                elif "lead" in line.lower() and ("column" in line.lower() or ":" in line):
                    relationship_lines.append((i+1, line.strip()))
            
            if relationship_lines:
                print("  🔍 Relations avec les leads:")
                for line_num, line in relationship_lines:
                    print(f"    Ligne {line_num}: {line}")
                
                # Si on trouve des relations, on modifie le modèle pour utiliser les IDs des leads
                if "relationship" in ''.join([line for _, line in relationship_lines]):
                    with open(campaigns_model_path, 'r') as f:
                        model_content = f.read()
                        original_content = model_content
                    
                    # Chercher et modifier les relations
                    lines = model_content.split('\n')
                    modified_lines = []
                    fixed = False
                    
                    for i, line in enumerate(lines):
                        if "relationship" in line.lower() and "lead" in line.lower():
                            # Modifier la relation pour renvoyer des IDs au lieu d'objets
                            # Par exemple: relationship("Lead", back_populates="campaign")
                            # => relationship("Lead", back_populates="campaign", lazy="selectin")
                            if "lazy" not in line:
                                indent = len(line) - len(line.lstrip())
                                spaces = ' ' * indent
                                if ")" in line:
                                    modified_line = line.replace(")", ", lazy='selectin')")
                                    modified_lines.append(modified_line)
                                    fixed = True
                                    print(f"  ✅ Modification de la relation lead (lazy loading): Ligne {i+1}")
                                else:
                                    modified_lines.append(line)
                            else:
                                modified_lines.append(line)
                        else:
                            modified_lines.append(line)
                    
                    if fixed:
                        # Sauvegarder les modifications
                        backup_path = f"{campaigns_model_path}.bak"
                        os.rename(campaigns_model_path, backup_path)
                        
                        with open(campaigns_model_path, 'w') as f:
                            f.write('\n'.join(modified_lines))
                        
                        print(f"✅ Modifications appliquées au modèle de campagne")
                        print(f"📋 Sauvegarde du fichier original: {os.path.relpath(backup_path, BERINIA_BACKEND_PATH)}")
                    else:
                        print("⚠️ Aucune modification nécessaire pour le modèle de campagne")
            else:
                print("  ⚠️ Aucune relation avec les leads trouvée dans le modèle de campagne")
    
    # 3. Chercher et corriger les routes API qui retournent des campagnes avec des leads
    endpoints_dir = os.path.join(BERINIA_BACKEND_PATH, "app", "api", "endpoints")
    if not os.path.exists(endpoints_dir):
        print(f"❌ Répertoire des endpoints introuvable: {endpoints_dir}")
    else:
        print("\n🔍 Recherche des endpoints de campagne...")
        campaign_endpoints = []
        
        for root, dirs, files in os.walk(endpoints_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if ("campaign" in content.lower() or "Campaign" in content) and "router" in content:
                            campaign_endpoints.append(filepath)
                            print(f"✅ Endpoint de campagne trouvé: {os.path.relpath(filepath, BERINIA_BACKEND_PATH)}")
        
        for endpoint in campaign_endpoints:
            print(f"\n📄 Analyse de l'endpoint: {os.path.relpath(endpoint, BERINIA_BACKEND_PATH)}")
            with open(endpoint, 'r') as f:
                content = f.read()
                original_content = content
            
            # Chercher les fonctions qui retournent des campagnes
            lines = content.split('\n')
            functions = []
            current_function = []
            in_function = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith("def ") and "campaign" in line.lower():
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
            
            # Analyser les fonctions qui retournent des campagnes avec des leads
            modified_lines = lines.copy()
            modifications_made = False
            
            for function in functions:
                function_lines = [lines[i] for i in function]
                function_text = '\n'.join(function_lines)
                
                # Chercher les retours de campagne qui incluent des leads
                if "lead" in function_text.lower() and "return" in function_text:
                    # Trouver le nom de la fonction
                    func_name = ""
                    for line in function_lines:
                        if line.strip().startswith("def "):
                            func_name = line.strip().split("def ")[1].split("(")[0].strip()
                            break
                    
                    print(f"  🔍 Fonction {func_name} peut retourner des campagnes avec leads")
                    
                    # Chercher les retours qui incluent directement des objets Lead
                    for i in function:
                        line = lines[i]
                        if "return" in line and not "return_" in line:
                            # Si on retourne un dictionnaire ou une liste
                            if ("{" in line or "[" in line) and "leads" in line:
                                # On inspecte le bloc de retour en entier
                                return_block_start = i
                                return_block_end = i
                                brace_count = 0
                                
                                # Calculer le nombre d'accolades/crochets ouverts et fermés
                                for j in range(i, min(len(lines), i+20)):
                                    line_j = lines[j]
                                    brace_count += line_j.count("{") + line_j.count("[")
                                    brace_count -= line_j.count("}") + line_j.count("]")
                                    
                                    if brace_count == 0 and j > i:
                                        return_block_end = j
                                        break
                                
                                # Analyser le bloc de retour
                                return_block = lines[return_block_start:return_block_end+1]
                                return_text = '\n'.join(return_block)
                                
                                # Si le bloc contient des leads, il faut le modifier
                                if "leads" in return_text and not "lead_ids" in return_text:
                                    print(f"  🔧 Correction du bloc de retour ligne {return_block_start+1}-{return_block_end+1}")
                                    
                                    # Deux approches possibles :
                                    # 1. Si le bloc est simple, on remplace les leads par leurs IDs
                                    # 2. Si le bloc est complexe, on ajoute une transformation avant le retour
                                    
                                    # On va insérer une transformation avant le bloc de retour
                                    indent = len(lines[return_block_start]) - len(lines[return_block_start].lstrip())
                                    spaces = ' ' * indent
                                    lead_transform = f"{spaces}# Transformation des leads en IDs pour éviter l'erreur de sérialisation\n"
                                    lead_transform += f"{spaces}if 'leads' in locals() and leads:\n"
                                    lead_transform += f"{spaces}    lead_ids = [lead.id for lead in leads]\n"
                                    
                                    # Modifier le bloc de retour pour utiliser lead_ids
                                    modified_return_block = []
                                    for line_j in return_block:
                                        if "'leads'" in line_j or '"leads"' in line_j:
                                            # Remplacer la référence aux leads par lead_ids
                                            if ":" in line_j:
                                                key_part = line_j.split(":")[0]
                                                indent_j = len(line_j) - len(line_j.lstrip())
                                                spaces_j = ' ' * indent_j
                                                modified_return_block.append(f"{spaces_j}{key_part}: lead_ids,")
                                                modifications_made = True
                                            else:
                                                modified_return_block.append(line_j)
                                        else:
                                            modified_return_block.append(line_j)
                                    
                                    # Mise à jour des lignes
                                    for j in range(return_block_start, return_block_end+1):
                                        modified_lines[j] = ""  # Effacer les lignes originales
                                    
                                    # Insérer la transformation et le bloc modifié
                                    modified_lines[return_block_start] = lead_transform
                                    for idx, line_j in enumerate(modified_return_block):
                                        modified_lines.insert(return_block_start + 1 + idx, line_j)
                                    
                                    print(f"  ✅ Ajout d'une transformation des leads en IDs avant le retour")
            
            # Appliquer les modifications si nécessaire
            if modifications_made:
                backup_path = f"{endpoint}.bak"
                os.rename(endpoint, backup_path)
                
                with open(endpoint, 'w') as f:
                    f.write('\n'.join(modified_lines))
                
                print(f"✅ Corrections appliquées à l'endpoint: {os.path.relpath(endpoint, BERINIA_BACKEND_PATH)}")
                print(f"📋 Sauvegarde du fichier original: {os.path.relpath(backup_path, BERINIA_BACKEND_PATH)}")
    
    return True

if __name__ == "__main__":
    print(f"\n{'='*40}")
    print(f"🔧 UTILITAIRE DE CORRECTION DES LEADS DANS L'API BERINIA")
    print(f"🕒 Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}\n")
    
    # Vérifier le chemin d'accès à Berinia
    if not is_berinia_available():
        print("❌ Backend Berinia non disponible.")
        print(f"Le chemin défini est: {BERINIA_BACKEND_PATH}")
        print("Vous pouvez modifier ce chemin en définissant la variable d'environnement BERINIA_BACKEND_PATH")
        print("Par exemple: export BERINIA_BACKEND_PATH=/chemin/vers/berinia/backend")
        sys.exit(1)
    
    print("📂 Inspections des chemins d'accès au backend Berinia...")
    examine_berinia_api_source()
    
    print("\n🔍 Analyse des modèles et des relations...")
    find_and_fix_model_code()
    
    print("\n🔧 Correction des endpoints API...")
    fix_api_leads_serialization()
    
    print("\n✅ Opérations terminées.")
    print("\n🚀 Pour redémarrer le système avec les corrections, exécutez:")
    print("python3 start_brain_agent.py")
