#!/usr/bin/env python3
import os
import sys
import json
import time
import datetime
import re
import shutil
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("smart_debugger.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SmartDebugger")

class VectorMemory:
    """Mémoire vectorielle pour stocker les expériences de l'agent."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2", memory_file="debugger_memory.json"):
        self.model = SentenceTransformer(model_name)
        self.memory_file = memory_file
        self.memories = self._load_memories()
        
    def _load_memories(self) -> List[Dict[str, Any]]:
        """Charge les souvenirs depuis le fichier de mémoire."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f"Impossible de charger le fichier mémoire: {self.memory_file}. Création d'une nouvelle mémoire.")
                return []
        return []
    
    def _save_memories(self) -> None:
        """Sauvegarde les souvenirs dans le fichier de mémoire."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def add_memory(self, 
                  problem: str, 
                  solution: str, 
                  outcome: str, 
                  feedback: Optional[str] = None, 
                  files_modified: Optional[List[str]] = None,
                  code_changes: Optional[Dict[str, str]] = None) -> None:
        """Ajoute une nouvelle expérience à la mémoire."""
        if files_modified is None:
            files_modified = []
        if code_changes is None:
            code_changes = {}
            
        # Création d'un texte pour l'embedding
        text_to_embed = f"Problème: {problem}\nSolution: {solution}\nOutcome: {outcome}"
        
        # Génération de l'embedding
        embedding = self.model.encode(text_to_embed).tolist()
        
        # Création du souvenir
        memory = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "problem": problem,
            "solution": solution,
            "outcome": outcome,
            "feedback": feedback,
            "files_modified": files_modified,
            "code_changes": code_changes,
            "embedding": embedding
        }
        
        self.memories.append(memory)
        self._save_memories()
        logger.info(f"Nouvelle expérience ajoutée à la mémoire: {problem[:50]}...")
    
    def update_feedback(self, memory_id: str, feedback: str) -> bool:
        """Met à jour le feedback pour une mémoire spécifique."""
        for memory in self.memories:
            if memory["id"] == memory_id:
                memory["feedback"] = feedback
                self._save_memories()
                logger.info(f"Feedback mis à jour pour la mémoire {memory_id}: {feedback}")
                return True
        logger.warning(f"Impossible de trouver la mémoire avec l'ID {memory_id}")
        return False
    
    def find_similar_experiences(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Trouve des expériences similaires basées sur la requête."""
        if not self.memories:
            return []
        
        # Génération de l'embedding pour la requête
        query_embedding = self.model.encode(query).reshape(1, -1)
        
        # Extraction des embeddings existants
        memory_embeddings = np.array([memory["embedding"] for memory in self.memories])
        
        # Calcul de la similarité
        similarities = cosine_similarity(query_embedding, memory_embeddings)[0]
        
        # Tri des souvenirs par similarité
        sorted_indices = similarities.argsort()[::-1][:top_k]
        
        return [
            {**self.memories[idx], "similarity": float(similarities[idx])}
            for idx in sorted_indices
            if similarities[idx] > 0.5  # Seuil de similarité minimal
        ]

class SmartDebugger:
    """Agent intelligent de débogage qui apprend de ses expériences."""
    
    def __init__(self):
        self.memory = VectorMemory()
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.datetime.now()
        self.files_modified = []
        self.code_changes = {}
        
    def analyze_error(self, error_message: str, file_path: Optional[str] = None, code_context: Optional[str] = None) -> Dict[str, Any]:
        """Analyse une erreur et propose des solutions basées sur l'expérience passée."""
        logger.info(f"Analyse de l'erreur: {error_message[:100]}...")
        
        # Construction de la requête
        query = f"Erreur: {error_message}"
        if file_path:
            query += f"\nFichier: {file_path}"
        if code_context:
            query += f"\nContexte: {code_context}"
            
        # Recherche d'expériences similaires
        similar_experiences = self.memory.find_similar_experiences(query)
        
        # Préparation de la réponse
        response = {
            "error": error_message,
            "file_path": file_path,
            "similar_experiences": similar_experiences,
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": self.current_session_id
        }
        
        # Si des expériences similaires sont trouvées, ajouter des recommandations
        if similar_experiences:
            # Privilégier les expériences avec un feedback positif
            positive_experiences = [exp for exp in similar_experiences if exp.get("feedback") == "positive"]
            if positive_experiences:
                best_experience = positive_experiences[0]
            else:
                best_experience = similar_experiences[0]
                
            response["recommended_solution"] = best_experience["solution"]
            response["confidence"] = best_experience["similarity"]
            response["experience_id"] = best_experience["id"]
            
            logger.info(f"Solution recommandée basée sur l'expérience {best_experience['id']} avec une confiance de {best_experience['similarity']:.2f}")
        else:
            response["recommended_solution"] = "Aucune solution automatique trouvée. Analyse manuelle requise."
            response["confidence"] = 0.0
            logger.info("Aucune expérience similaire trouvée. Analyse manuelle requise.")
            
        return response
    
    def fix_indentation_issues(self, file_path: str) -> Tuple[bool, str]:
        """Corrige les problèmes d'indentation dans un fichier Python."""
        if not os.path.exists(file_path):
            return False, f"Le fichier {file_path} n'existe pas."
            
        # Créer une sauvegarde
        backup_path = f"{file_path}.indent.bak"
        shutil.copy2(file_path, backup_path)
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Analyse de l'indentation
            fixed_lines = []
            current_block_indent = 0
            in_function = False
            function_indent = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Ignorer les lignes vides
                if not stripped:
                    fixed_lines.append(line)
                    continue
                    
                # Détecter le début d'une fonction ou d'une classe
                if re.match(r'^(def|class)\s+\w+', stripped):
                    in_function = True
                    function_indent = len(line) - len(line.lstrip())
                    current_block_indent = function_indent + 4
                    fixed_lines.append(line)
                    continue
                
                # Détecter les blocs conditionnels ou les boucles
                if in_function and re.match(r'^(if|elif|else|for|while|try|except|finally)\b', stripped):
                    if not stripped.endswith(':'):
                        # Corriger les blocs sans : à la fin
                        line = line.rstrip() + ':\n'
                    
                    # Calculer l'indentation attendue
                    expected_indent = ' ' * current_block_indent
                    actual_indent = line[:len(line) - len(line.lstrip())]
                    
                    if len(actual_indent) != current_block_indent:
                        # Corriger l'indentation
                        line = expected_indent + line.lstrip()
                    
                    current_block_indent += 4
                    fixed_lines.append(line)
                    continue
                
                # Détecter la fin d'un bloc
                if in_function and stripped == '}' or stripped == 'return':
                    current_block_indent = max(function_indent + 4, current_block_indent - 4)
                    
                    # Calculer l'indentation attendue
                    expected_indent = ' ' * current_block_indent
                    actual_indent = line[:len(line) - len(line.lstrip())]
                    
                    if len(actual_indent) != current_block_indent:
                        # Corriger l'indentation
                        line = expected_indent + line.lstrip()
                        
                    fixed_lines.append(line)
                    continue
                
                # Lignes normales dans une fonction
                if in_function:
                    # Calculer l'indentation attendue
                    expected_indent = ' ' * current_block_indent
                    actual_indent = line[:len(line) - len(line.lstrip())]
                    
                    if len(actual_indent) != current_block_indent:
                        # Corriger l'indentation
                        line = expected_indent + line.lstrip()
                        
                fixed_lines.append(line)
            
            # Écrire le contenu corrigé
            with open(file_path, 'w') as f:
                f.writelines(fixed_lines)
                
            # Enregistrer la modification
            self.files_modified.append(file_path)
            diff = "".join(lines) + "\n===>\n" + "".join(fixed_lines)
            self.code_changes[file_path] = diff
            
            return True, f"Indentation corrigée dans {file_path}"
            
        except Exception as e:
            # Restaurer la sauvegarde en cas d'erreur
            shutil.copy2(backup_path, file_path)
            return False, f"Erreur lors de la correction de l'indentation: {str(e)}"
    
    def add_jsonable_encoder_fix(self, file_path: str) -> Tuple[bool, str]:
        """Ajoute jsonable_encoder pour corriger les erreurs de sérialisation SQLAlchemy."""
        if not os.path.exists(file_path):
            return False, f"Le fichier {file_path} n'existe pas."
            
        # Créer une sauvegarde
        backup_path = f"{file_path}.json.bak"
        shutil.copy2(file_path, backup_path)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Vérifier si jsonable_encoder est déjà importé
            if "from fastapi.encoders import jsonable_encoder" not in content:
                # Ajouter l'import
                import_end = content.find("\n\n", content.find("import "))
                if import_end == -1:
                    import_end = content.find("router = APIRouter")
                    
                if import_end != -1:
                    content = content[:import_end] + "\nfrom fastapi.encoders import jsonable_encoder" + content[import_end:]
            
            # Remplacer les return directs par des return avec jsonable_encoder
            content = re.sub(
                r'return ([a-zA-Z_][a-zA-Z0-9_]*)',
                r'return jsonable_encoder(\1)',
                content
            )
            
            # Éviter les doubles jsonable_encoder
            content = content.replace('jsonable_encoder(jsonable_encoder(', 'jsonable_encoder(')
            
            # Écrire le contenu modifié
            with open(file_path, 'w') as f:
                f.write(content)
                
            # Enregistrer la modification
            self.files_modified.append(file_path)
            
            # Lire le contenu original pour le diff
            with open(backup_path, 'r') as f:
                original_content = f.read()
                
            diff = original_content + "\n===>\n" + content
            self.code_changes[file_path] = diff
            
            return True, f"jsonable_encoder ajouté dans {file_path}"
            
        except Exception as e:
            # Restaurer la sauvegarde en cas d'erreur
            shutil.copy2(backup_path, file_path)
            return False, f"Erreur lors de l'ajout de jsonable_encoder: {str(e)}"
    
    def fix_router_definition(self, file_path: str, remove_prefix: bool = False) -> Tuple[bool, str]:
        """Corrige ou ajoute la définition du router."""
        if not os.path.exists(file_path):
            return False, f"Le fichier {file_path} n'existe pas."
            
        # Créer une sauvegarde
        backup_path = f"{file_path}.router.bak"
        shutil.copy2(file_path, backup_path)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            filename = os.path.basename(file_path)
            base_name = filename.replace(".py", "")
            
            # Vérifier si le router est défini
            if "router = APIRouter" not in content:
                # Le router n'est pas défini, l'ajouter
                import_end = content.find("\n\n", content.find("import "))
                if import_end == -1:
                    # Chercher la première fonction
                    import_end = content.find("@")
                    if import_end == -1:
                        import_end = content.find("def ")
                    
                    if import_end != -1:
                        # Trouver le début de la ligne
                        line_start = content.rfind("\n", 0, import_end) + 1
                        router_def = f"router = APIRouter()\n\n"
                        content = content[:line_start] + router_def + content[line_start:]
                else:
                    router_def = f"router = APIRouter()\n\n"
                    content = content[:import_end] + "\n" + router_def + content[import_end:]
            elif "# router = APIRouter" in content:
                # Le router est commenté, le décommenter
                content = content.replace("# router = APIRouter", "router = APIRouter")
            elif remove_prefix and "router = APIRouter(prefix=" in content:
                # Supprimer le préfixe pour éviter la duplication
                content = re.sub(
                    r'router = APIRouter\(prefix="[^"]+", tags=\["[^"]+"\]\)',
                    r'router = APIRouter()',
                    content
                )
                
            # Écrire le contenu modifié
            with open(file_path, 'w') as f:
                f.write(content)
                
            # Enregistrer la modification
            self.files_modified.append(file_path)
            
            # Lire le contenu original pour le diff
            with open(backup_path, 'r') as f:
                original_content = f.read()
                
            diff = original_content + "\n===>\n" + content
            self.code_changes[file_path] = diff
            
            return True, f"Définition du router corrigée dans {file_path}"
            
        except Exception as e:
            # Restaurer la sauvegarde en cas d'erreur
            shutil.copy2(backup_path, file_path)
            return False, f"Erreur lors de la correction du router: {str(e)}"
    
    def apply_fix(self, error_type: str, file_path: str) -> Dict[str, Any]:
        """Applique une correction basée sur le type d'erreur identifié."""
        logger.info(f"Application d'une correction pour l'erreur '{error_type}' dans {file_path}")
        
        result = {
            "error_type": error_type,
            "file_path": file_path,
            "success": False,
            "message": "",
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": self.current_session_id
        }
        
        try:
            if error_type == "indentation":
                success, message = self.fix_indentation_issues(file_path)
            elif error_type == "sa_instance_state":
                success, message = self.add_jsonable_encoder_fix(file_path)
            elif error_type == "router_not_defined":
                success, message = self.fix_router_definition(file_path)
            elif error_type == "router_prefix_duplicate":
                success, message = self.fix_router_definition(file_path, remove_prefix=True)
            else:
                success, message = False, f"Type d'erreur inconnu: {error_type}"
                
            result["success"] = success
            result["message"] = message
            
            # Enregistrer l'expérience dans la mémoire
            if success:
                self.memory.add_memory(
                    problem=error_type,
                    solution=f"Correction appliquée pour {error_type} dans {file_path}",
                    outcome="success",
                    files_modified=self.files_modified,
                    code_changes=self.code_changes
                )
                
        except Exception as e:
            result["success"] = False
            result["message"] = f"Erreur lors de l'application de la correction: {str(e)}"
            
            # Enregistrer l'échec dans la mémoire
            self.memory.add_memory(
                problem=error_type,
                solution=f"Tentative de correction pour {error_type} dans {file_path}",
                outcome="failure",
                files_modified=self.files_modified,
                code_changes=self.code_changes
            )
            
        return result
    
    def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport détaillé de la session de débogage."""
        session_duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
        
        report = {
            "session_id": self.current_session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "session_start": self.session_start_time.isoformat(),
            "session_duration_seconds": session_duration,
            "files_modified": self.files_modified,
            "fixes_applied": len(self.files_modified),
            "detailed_changes": {}
        }
        
        # Inclure les détails des modifications
        for file_path, diff in self.code_changes.items():
            report["detailed_changes"][file_path] = {
                "diff_summary": diff[:200] + "..." if len(diff) > 200 else diff,
                "full_diff_available": len(diff) > 200
            }
            
        return report
    
    def save_feedback(self, memory_id: str, feedback: str) -> bool:
        """Enregistre le feedback de l'utilisateur pour une correction spécifique."""
        return self.memory.update_feedback(memory_id, feedback)

    def reset_session(self) -> None:
        """Réinitialise la session courante."""
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.datetime.now()
        self.files_modified = []
        self.code_changes = {}
        logger.info(f"Nouvelle session démarrée: {self.current_session_id}")

def main():
    parser = argparse.ArgumentParser(description="Agent intelligent de débogage pour applications Python.")
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")
    
    # Commande d'analyse
    analyze_parser = subparsers.add_parser("analyze", help="Analyser une erreur")
    analyze_parser.add_argument("--error", required=True, help="Message d'erreur à analyser")
    analyze_parser.add_argument("--file", help="Fichier dans lequel l'erreur s'est produite")
    analyze_parser.add_argument("--context", help="Contexte du code où l'erreur s'est produite")
    
    # Commande de correction
    fix_parser = subparsers.add_parser("fix", help="Appliquer une correction")
    fix_parser.add_argument("--type", required=True, choices=["indentation", "sa_instance_state", "router_not_defined", "router_prefix_duplicate"], help="Type d'erreur à corriger")
    fix_parser.add_argument("--file", required=True, help="Fichier sur lequel appliquer la correction")
    
    # Commande de rapport
    report_parser = subparsers.add_parser("report", help="Générer un rapport")
    
    # Commande de feedback
    feedback_parser = subparsers.add_parser("feedback", help="Enregistrer un feedback")
    feedback_parser.add_argument("--id", required=True, help="ID de la mémoire")
    feedback_parser.add_argument("--feedback", required=True, choices=["positive", "negative"], help="Feedback sur la correction")
    
    # Commande de reset
    reset_parser = subparsers.add_parser("reset", help="Réinitialiser la session")
    
    args = parser.parse_args()
    
    # Instancier l'agent
    agent = SmartDebugger()
    
    if args.command == "analyze":
        result = agent.analyze_error(args.error, args.file, args.context)
        print(json.dumps(result, indent=2))
    elif args.command == "fix":
        result = agent.apply_fix(args.type, args.file)
        print(json.dumps(result, indent=2))
    elif args.command == "report":
        report = agent.generate_report()
        print(json.dumps(report, indent=2))
    elif args.command == "feedback":
        success = agent.save_feedback(args.id, args.feedback)
        print(json.dumps({"success": success}, indent=2))
    elif args.command == "reset":
        agent.reset_session()
        print(json.dumps({"success": True, "message": "Session réinitialisée"}, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
