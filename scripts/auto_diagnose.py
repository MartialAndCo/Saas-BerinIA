#!/usr/bin/env python3
"""
Script d'auto-diagnostic pour les applications FastAPI

Ce script analyse automatiquement les journaux et le code pour détecter
et corriger les problèmes courants dans les applications FastAPI.
"""

import os
import sys
import re
import json
import argparse
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Importer l'agent intelligent
try:
    from smart_debugger_agent import SmartDebugger
except ImportError:
    print("Agent Smart Debugger non trouvé, l'installation sera effectuée automatiquement.")
    import pip
    pip.main(['install', 'numpy', 'scikit-learn', 'sentence-transformers'])
    print("Dépendances installées.")

class FastAPIDiagnostic:
    """Outil de diagnostic automatique pour applications FastAPI."""
    
    # Patterns d'erreurs connus
    ERROR_PATTERNS = {
        "indentation": [
            r"IndentationError: .*",
            r"expected an indented block",
            r"unexpected indent"
        ],
        "sa_instance_state": [
            r"'dict' object has no attribute '_sa_instance_state'",
            r"AttributeError: '_sa_instance_state'"
        ],
        "router_not_defined": [
            r"NameError: name 'router' is not defined"
        ],
        "router_prefix_duplicate": [
            r"Not Found",  # Simple 404, peut indiquer un problème de route
            r"Cannot include router .* in router .* with the same prefix"
        ]
    }
    
    def __init__(self, project_path: str, log_path: Optional[str] = None):
        """Initialize diagnostic tool."""
        self.project_path = os.path.abspath(project_path)
        self.log_path = log_path
        self.debugger = SmartDebugger()
        self.issues_found = []
        self.fixes_applied = []
        
    def scan_logs(self) -> List[Dict[str, Any]]:
        """Scan logs for known errors."""
        if not self.log_path or not os.path.exists(self.log_path):
            print(f"Pas de fichier log spécifié ou introuvable: {self.log_path}")
            return []
            
        issues = []
        
        with open(self.log_path, 'r') as f:
            log_content = f.read()
            
        # Rechercher les patterns d'erreurs connus
        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, log_content)
                for match in matches:
                    # Extraire le contexte autour de l'erreur
                    start = max(0, match.start() - 200)
                    end = min(len(log_content), match.end() + 200)
                    error_context = log_content[start:end]
                    
                    # Essayer de trouver le fichier concerné
                    file_match = re.search(r'File "([^"]+)"', error_context)
                    file_path = file_match.group(1) if file_match else None
                    
                    issues.append({
                        "error_type": error_type,
                        "error_message": match.group(0),
                        "context": error_context,
                        "file_path": file_path,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return issues
    
    def scan_endpoints(self) -> List[Dict[str, Any]]:
        """Scan FastAPI endpoint files for potential issues."""
        issues = []
        
        # Trouver tous les fichiers Python
        python_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        # Analyser chaque fichier pour détecter des problèmes potentiels
        for file_path in python_files:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Vérifier si c'est un fichier d'endpoints FastAPI
            if "from fastapi import" in content and "APIRouter" in content:
                # Vérifier les problèmes de router
                if "@router" in content and not re.search(r'router\s*=\s*APIRouter', content):
                    issues.append({
                        "error_type": "router_not_defined",
                        "error_message": "router utilisé mais non défini",
                        "file_path": file_path,
                        "context": "Le fichier utilise @router mais ne définit pas router = APIRouter()",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Vérifier les doubles préfixes
                if re.search(r'router\s*=\s*APIRouter\(prefix="', content) and "include_router" in content:
                    issues.append({
                        "error_type": "router_prefix_duplicate",
                        "error_message": "Risque de duplication de préfixes",
                        "file_path": file_path,
                        "context": "Le router définit un préfixe localement, qui pourrait être dupliqué lors de l'inclusion",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Vérifier la sérialisation SQLAlchemy
                if "return " in content and "jsonable_encoder" not in content and ("SQLAlchemy" in content or "Base" in content):
                    issues.append({
                        "error_type": "sa_instance_state",
                        "error_message": "Risque d'erreur de sérialisation SQLAlchemy",
                        "file_path": file_path,
                        "context": "Le fichier retourne des objets SQLAlchemy sans utiliser jsonable_encoder",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return issues
    
    def run_service_diagnostic(self, service_name: str) -> List[Dict[str, Any]]:
        """Run diagnostic on a systemd service."""
        issues = []
        
        try:
            # Récupérer le journal du service
            result = subprocess.run(
                ["journalctl", "-u", service_name, "-n", "500", "--no-pager"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Erreur lors de la récupération des journaux du service {service_name}")
                return []
                
            log_content = result.stdout
            
            # Analysez les journaux pour les erreurs connues
            for error_type, patterns in self.ERROR_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, log_content)
                    for match in matches:
                        # Extraire le contexte autour de l'erreur
                        start = max(0, match.start() - 200)
                        end = min(len(log_content), match.end() + 200)
                        error_context = log_content[start:end]
                        
                        # Essayer de trouver le fichier concerné
                        file_match = re.search(r'File "([^"]+)"', error_context)
                        file_path = file_match.group(1) if file_match else None
                        
                        issues.append({
                            "error_type": error_type,
                            "error_message": match.group(0),
                            "context": error_context,
                            "file_path": file_path,
                            "service_name": service_name,
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Vérifier l'état du service
            status_result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True
            )
            
            if "Active: failed" in status_result.stdout:
                issues.append({
                    "error_type": "service_failed",
                    "error_message": f"Le service {service_name} est en état d'échec",
                    "context": status_result.stdout,
                    "service_name": service_name,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"Erreur lors du diagnostic du service {service_name}: {str(e)}")
            
        return issues
    
    def analyze_all(self) -> List[Dict[str, Any]]:
        """Run all diagnostics."""
        self.issues_found = []
        
        # Scanner les logs si spécifiés
        if self.log_path:
            log_issues = self.scan_logs()
            self.issues_found.extend(log_issues)
            
        # Scanner les fichiers d'endpoints
        endpoint_issues = self.scan_endpoints()
        self.issues_found.extend(endpoint_issues)
        
        return self.issues_found
    
    def fix_issues(self, auto_fix: bool = False) -> List[Dict[str, Any]]:
        """Fix detected issues."""
        self.fixes_applied = []
        
        for issue in self.issues_found:
            error_type = issue.get("error_type")
            file_path = issue.get("file_path")
            
            if not file_path or not os.path.exists(file_path):
                continue
                
            print(f"Analyse de l'erreur: {error_type} dans {file_path}")
            
            # Analyse approfondie avec l'agent intelligent
            analysis = self.debugger.analyze_error(
                error_message=issue.get("error_message", ""),
                file_path=file_path,
                code_context=issue.get("context", "")
            )
            
            # Décider de la correction
            if auto_fix:
                if error_type in ["indentation", "sa_instance_state", "router_not_defined", "router_prefix_duplicate"]:
                    result = self.debugger.apply_fix(error_type, file_path)
                    
                    if result["success"]:
                        self.fixes_applied.append({
                            "issue": issue,
                            "fix_result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                        print(f"✅ Correction appliquée: {result['message']}")
                    else:
                        print(f"❌ Échec de la correction: {result['message']}")
            else:
                print(f"Solution recommandée: {analysis.get('recommended_solution', 'Analyse manuelle requise')}")
                print(f"Confiance: {analysis.get('confidence', 0)}")
                
                if "experience_id" in analysis:
                    print(f"Basé sur l'expérience: {analysis['experience_id']}")
                    
                apply_fix = input("Appliquer la correction? (o/n): ").lower() == 'o'
                
                if apply_fix:
                    result = self.debugger.apply_fix(error_type, file_path)
                    
                    if result["success"]:
                        self.fixes_applied.append({
                            "issue": issue,
                            "fix_result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                        print(f"✅ Correction appliquée: {result['message']}")
                        
                        # Demander un feedback
                        if "experience_id" in analysis:
                            feedback = input("La correction a-t-elle fonctionné? (o/n): ").lower() == 'o'
                            self.debugger.save_feedback(
                                analysis["experience_id"], 
                                "positive" if feedback else "negative"
                            )
                    else:
                        print(f"❌ Échec de la correction: {result['message']}")
        
        return self.fixes_applied
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report."""
        report = self.debugger.generate_report()
        
        # Ajouter des détails spécifiques au diagnostic
        report["issues_found"] = len(self.issues_found)
        report["issues_fixed"] = len(self.fixes_applied)
        report["issues_details"] = self.issues_found
        report["fixes_details"] = self.fixes_applied
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Diagnostic automatique pour applications FastAPI")
    parser.add_argument("--project", required=True, help="Chemin du projet à analyser")
    parser.add_argument("--log", help="Chemin du fichier log à analyser")
    parser.add_argument("--service", help="Nom du service systemd à analyser")
    parser.add_argument("--auto-fix", action="store_true", help="Appliquer automatiquement les corrections")
    parser.add_argument("--report", help="Chemin où enregistrer le rapport (format JSON)")
    
    args = parser.parse_args()
    
    # Initialisation du diagnostic
    diagnostic = FastAPIDiagnostic(project_path=args.project, log_path=args.log)
    
    print(f"📋 Démarrage du diagnostic pour {args.project}")
    
    # Diagnostic du service si spécifié
    if args.service:
        print(f"🔍 Analyse du service {args.service}...")
        service_issues = diagnostic.run_service_diagnostic(args.service)
        diagnostic.issues_found.extend(service_issues)
    
    # Diagnostic complet
    print("🔍 Analyse des fichiers et journaux...")
    issues = diagnostic.analyze_all()
    
    if not issues:
        print("✅ Aucun problème détecté!")
        return
        
    print(f"⚠️ {len(issues)} problèmes détectés:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue['error_type']} dans {issue.get('file_path', 'inconnu')}")
        print(f"     Message: {issue['error_message'][:100]}...")
        
    # Correction des problèmes
    if args.auto_fix or input("\nVoulez-vous tenter de corriger les problèmes? (o/n): ").lower() == 'o':
        print("\n🔧 Application des corrections...")
        fixes = diagnostic.fix_issues(auto_fix=args.auto_fix)
        
        if fixes:
            print(f"✅ {len(fixes)} corrections appliquées avec succès!")
        else:
            print("❌ Aucune correction n'a pu être appliquée.")
    
    # Génération du rapport
    report = diagnostic.generate_report()
    
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📊 Rapport enregistré dans {args.report}")
    else:
        print("\n📊 Résumé du rapport:")
        print(f"  - Session: {report['session_id']}")
        print(f"  - Problèmes détectés: {report['issues_found']}")
        print(f"  - Corrections appliquées: {report['issues_fixed']}")
        print(f"  - Fichiers modifiés: {len(report['files_modified'])}")
        
        if report['files_modified']:
            print("\n📄 Fichiers modifiés:")
            for file in report['files_modified']:
                print(f"  - {file}")

if __name__ == "__main__":
    main()
