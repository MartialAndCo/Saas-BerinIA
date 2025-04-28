#!/usr/bin/env python3
"""
Script de réparation intelligent pour l'API Berinia

Ce script utilise l'agent intelligent pour analyser et corriger automatiquement
les problèmes courants dans l'API Berinia. Il alimente également une base de connaissances
pour améliorer les futurs diagnostics.
"""

import os
import sys
import json
import argparse
import datetime
import subprocess
from typing import Dict, List, Any, Optional

try:
    from smart_debugger_agent import SmartDebugger
except ImportError:
    print("Agent Smart Debugger non trouvé. Installation des dépendances...")
    import pip
    pip.main(['install', 'numpy', 'scikit-learn', 'sentence-transformers'])
    from smart_debugger_agent import SmartDebugger

# Configuration des chemins Berinia
BERINIA_ROOT = "/root/berinia"
BERINIA_BACKEND = os.path.join(BERINIA_ROOT, "backend")
BERINIA_FRONTEND = os.path.join(BERINIA_ROOT, "frontend")
BERINIA_API_SERVICE = "berinia-api.service"
BERINIA_ENDPOINTS_DIR = os.path.join(BERINIA_BACKEND, "app/api/endpoints")

class BeriniaIntelligentFixer:
    """Outil de réparation intelligent spécifique à Berinia."""
    
    def __init__(self):
        self.debugger = SmartDebugger()
        self.fixes_applied = []
        self.issues_found = []
        self.report_data = {}
    
    def check_service_status(self) -> Dict[str, Any]:
        """Vérifie l'état du service Berinia API."""
        try:
            result = subprocess.run(
                ["systemctl", "status", BERINIA_API_SERVICE],
                capture_output=True,
                text=True
            )
            
            is_running = "Active: active (running)" in result.stdout
            
            if not is_running:
                # Analyse des journaux pour trouver l'erreur
                log_result = subprocess.run(
                    ["journalctl", "-u", BERINIA_API_SERVICE, "-n", "100", "--no-pager"],
                    capture_output=True,
                    text=True
                )
                
                return {
                    "running": False,
                    "status_output": result.stdout,
                    "error_logs": log_result.stdout,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                return {
                    "running": True,
                    "status_output": result.stdout,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
        except Exception as e:
            return {
                "running": False,
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def analyze_service_issues(self) -> List[Dict[str, Any]]:
        """Analyse les journaux du service pour identifier les problèmes."""
        service_check = self.check_service_status()
        issues = []
        
        if not service_check["running"]:
            error_logs = service_check.get("error_logs", "")
            
            # Rechercher les erreurs connues
            if "NameError: name 'router' is not defined" in error_logs:
                # Trouver le fichier concerné
                file_match = re.search(r'File "([^"]+)"', error_logs)
                file_path = file_match.group(1) if file_match else None
                
                if file_path and os.path.exists(file_path):
                    issues.append({
                        "error_type": "router_not_defined",
                        "error_message": "Router non défini",
                        "file_path": file_path,
                        "context": error_logs,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
            
            elif "'dict' object has no attribute '_sa_instance_state'" in error_logs:
                # Trouver le fichier concerné
                file_match = re.search(r'File "([^"]+)"', error_logs)
                file_path = file_match.group(1) if file_match else None
                
                if file_path and os.path.exists(file_path):
                    issues.append({
                        "error_type": "sa_instance_state",
                        "error_message": "Erreur de sérialisation SQLAlchemy",
                        "file_path": file_path,
                        "context": error_logs,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
            
            elif "IndentationError" in error_logs:
                # Trouver le fichier concerné
                file_match = re.search(r'File "([^"]+)"', error_logs)
                file_path = file_match.group(1) if file_match else None
                
                if file_path and os.path.exists(file_path):
                    issues.append({
                        "error_type": "indentation",
                        "error_message": "Erreur d'indentation",
                        "file_path": file_path,
                        "context": error_logs,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
        
        return issues
    
    def scan_api_endpoints(self) -> List[Dict[str, Any]]:
        """Analyse les fichiers d'endpoints API pour détecter des problèmes potentiels."""
        issues = []
        
        # Parcourir tous les fichiers d'endpoints
        if os.path.exists(BERINIA_ENDPOINTS_DIR):
            python_files = [os.path.join(BERINIA_ENDPOINTS_DIR, f) for f in os.listdir(BERINIA_ENDPOINTS_DIR) if f.endswith(".py")]
            
            for file_path in python_files:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Vérifier les problèmes de router
                if "@router" in content and not re.search(r'router\s*=\s*APIRouter', content):
                    issues.append({
                        "error_type": "router_not_defined",
                        "error_message": "router utilisé mais non défini",
                        "file_path": file_path,
                        "context": "Le fichier utilise @router mais ne définit pas router = APIRouter()",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                
                # Vérifier les doubles préfixes
                if re.search(r'router\s*=\s*APIRouter\(prefix="', content) and "include_router" in content:
                    issues.append({
                        "error_type": "router_prefix_duplicate",
                        "error_message": "Risque de duplication de préfixes",
                        "file_path": file_path,
                        "context": "Le router définit un préfixe localement, qui pourrait être dupliqué lors de l'inclusion",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                
                # Vérifier la sérialisation SQLAlchemy
                if "return " in content and "jsonable_encoder" not in content and "from sqlalchemy" in content:
                    issues.append({
                        "error_type": "sa_instance_state",
                        "error_message": "Risque d'erreur de sérialisation SQLAlchemy",
                        "file_path": file_path,
                        "context": "Le fichier retourne des objets SQLAlchemy sans utiliser jsonable_encoder",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
        
        return issues
    
    def diagnose(self) -> List[Dict[str, Any]]:
        """Exécute le diagnostic complet de l'API Berinia."""
        self.issues_found = []
        
        # 1. Vérifier l'état du service
        service_issues = self.analyze_service_issues()
        self.issues_found.extend(service_issues)
        
        # 2. Analyser les fichiers d'endpoints
        endpoint_issues = self.scan_api_endpoints()
        self.issues_found.extend(endpoint_issues)
        
        return self.issues_found
    
    def fix_issues(self, auto_approve: bool = False) -> List[Dict[str, Any]]:
        """Corrige les problèmes détectés."""
        self.fixes_applied = []
        
        for issue in self.issues_found:
            error_type = issue.get("error_type")
            file_path = issue.get("file_path")
            
            if not file_path or not os.path.exists(file_path):
                continue
            
            print(f"\n🔍 Analyse du problème: {error_type} dans {file_path}")
            
            # Analyser le problème avec l'agent intelligent
            analysis = self.debugger.analyze_error(
                error_message=issue.get("error_message", ""),
                file_path=file_path,
                code_context=issue.get("context", "")
            )
            
            # Afficher l'analyse
            if analysis.get("similar_experiences"):
                print("🧠 Expériences similaires trouvées dans la mémoire")
                print(f"  Solution recommandée: {analysis.get('recommended_solution')}")
                print(f"  Confiance: {analysis.get('confidence', 0):.2f}")
            else:
                print("🆕 Aucune expérience similaire en mémoire")
            
            # Demander confirmation si nécessaire
            if auto_approve or input("\n⚙️ Appliquer la correction? (o/n): ").lower() == 'o':
                print(f"\n🔧 Application de la correction pour {error_type}...")
                
                result = self.debugger.apply_fix(error_type, file_path)
                
                if result["success"]:
                    print(f"✅ Correction appliquée avec succès: {result['message']}")
                    self.fixes_applied.append({
                        "issue": issue,
                        "fix_result": result,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    
                    # Demander un feedback
                    if "experience_id" in analysis and not auto_approve:
                        feedback = input("\n🤔 La correction vous semble-t-elle appropriée? (o/n): ").lower() == 'o'
                        self.debugger.save_feedback(
                            analysis["experience_id"], 
                            "positive" if feedback else "negative"
                        )
                        if feedback:
                            print("👍 Feedback positif enregistré - L'agent s'améliorera grâce à votre retour!")
                        else:
                            print("👎 Feedback négatif enregistré - L'agent essaiera d'autres approches à l'avenir.")
                else:
                    print(f"❌ Échec de la correction: {result['message']}")
        
        return self.fixes_applied
    
    def restart_service(self) -> bool:
        """Redémarre le service Berinia API."""
        if not self.fixes_applied:
            return False
            
        print("\n🔄 Redémarrage du service Berinia API...")
        
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", BERINIA_API_SERVICE],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Service redémarré avec succès")
                
                # Vérifier l'état du service après redémarrage
                time.sleep(3)  # Attendre quelques secondes pour le démarrage complet
                service_check = self.check_service_status()
                
                if service_check["running"]:
                    print("✅ Le service Berinia API est maintenant actif")
                    return True
                else:
                    print("❌ Le service n'a pas démarré correctement après redémarrage")
                    return False
            else:
                print(f"❌ Échec du redémarrage: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du redémarrage: {str(e)}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport complet du processus de diagnostic et correction."""
        debugger_report = self.debugger.generate_report()
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "berinia_root": BERINIA_ROOT,
            "issues_found": len(self.issues_found),
            "fixes_applied": len(self.fixes_applied),
            "issues_details": self.issues_found,
            "fixes_details": self.fixes_applied,
            "agent_memory_used": debugger_report.get("session_id"),
            "files_modified": debugger_report.get("files_modified", []),
            "service_status": self.check_service_status()
        }
        
        self.report_data = report
        return report
    
    def save_report(self, report_path: str) -> bool:
        """Sauvegarde le rapport dans un fichier JSON."""
        if not self.report_data:
            self.generate_report()
            
        try:
            with open(report_path, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            print(f"\n📊 Rapport enregistré dans {report_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement du rapport: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Outil de réparation intelligent pour l'API Berinia")
    parser.add_argument("--auto-approve", action="store_true", help="Appliquer automatiquement les corrections sans demander de confirmation")
    parser.add_argument("--report", help="Chemin où enregistrer le rapport de diagnostic")
    parser.add_argument("--no-restart", action="store_true", help="Ne pas redémarrer le service après les corrections")
    
    args = parser.parse_args()
    
    fixer = BeriniaIntelligentFixer()
    
    print("=" * 60)
    print("🤖 BERINIA INTELLIGENT FIXER 🤖")
    print("=" * 60)
    print(f"📂 Racine Berinia: {BERINIA_ROOT}")
    print(f"🔧 Mode: {'Automatique' if args.auto_approve else 'Interactif'}")
    print("=" * 60)
    
    # Diagnostic
    print("\n📋 Lancement du diagnostic...")
    issues = fixer.diagnose()
    
    if not issues:
        print("\n✅ Aucun problème détecté dans l'API Berinia!")
        
        # Vérifier quand même l'état du service
        service_status = fixer.check_service_status()
        if service_status["running"]:
            print("✅ Le service Berinia API fonctionne correctement")
        else:
            print("⚠️ Le service Berinia API n'est pas en cours d'exécution")
            if input("🔄 Souhaitez-vous démarrer le service? (o/n): ").lower() == 'o':
                subprocess.run(["sudo", "systemctl", "start", BERINIA_API_SERVICE])
                print("✅ Service démarré")
        
        return
    
    # Affichage des problèmes
    print(f"\n⚠️ {len(issues)} problèmes détectés:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue['error_type']} dans {issue.get('file_path', 'inconnu')}")
        print(f"     Message: {issue['error_message']}")
    
    # Correction des problèmes
    if args.auto_approve or input("\n🔧 Voulez-vous tenter de corriger les problèmes? (o/n): ").lower() == 'o':
        fixes = fixer.fix_issues(auto_approve=args.auto_approve)
        
        if fixes:
            print(f"\n🎉 {len(fixes)} corrections appliquées avec succès!")
            
            # Redémarrage du service
            if not args.no_restart:
                fixer.restart_service()
        else:
            print("\n❌ Aucune correction n'a pu être appliquée")
    
    # Génération du rapport
    report = fixer.generate_report()
    
    # Sauvegarde du rapport si demandée
    if args.report:
        fixer.save_report(args.report)
    
    # Résumé
    print("\n📊 Résumé des actions:")
    print(f"  - Problèmes détectés: {report['issues_found']}")
    print(f"  - Corrections appliquées: {len(report['fixes_details'])}")
    print(f"  - Fichiers modifiés: {len(report['files_modified'])}")
    
    if report['files_modified']:
        print("\n📄 Fichiers modifiés:")
        for file in report['files_modified']:
            print(f"  - {file}")
    
    print("\n🧠 L'agent a enregistré cette session dans sa mémoire et s'améliorera avec le temps")
    print("=" * 60)

if __name__ == "__main__":
    # Importer les modules nécessaires ici pour éviter les erreurs potentielles
    import re
    import time
    main()
