from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import json
import datetime
import os
import re

class AgentLoggerAgent(AgentBase):
    def __init__(self):
        super().__init__("AgentLoggerAgent")
        self.prompt_path = "prompts/agent_logger_agent_prompt.txt"
        self.logs_dir = "logs"
        self.reports_dir = "logs/reports"
        self.anomalies_file = "logs/anomalies_detected.json"
        self._ensure_directories_exist()
        
    def _ensure_directories_exist(self):
        """Ensures that necessary directories for logging and reporting exist"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, exist_ok=True)
        
        if not os.path.exists(self.anomalies_file):
            initial_anomalies = {
                "anomalies": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.anomalies_file, "w") as f:
                json.dump(initial_anomalies, f, indent=2)

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 📝 Gestion et analyse des logs...")
        
        # Extraire les paramètres d'entrée
        operation = input_data.get("operation", "analyze")
        target_agent = input_data.get("target_agent", "all")
        time_period = input_data.get("time_period", "today")
        
        # Préparer le résultat
        result = {
            "operation": operation,
            "target_agent": target_agent,
            "time_period": time_period,
            "status": "PROCESSING",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Charger le prompt
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
        except Exception as e:
            result = {
                "error": f"Erreur lors du chargement du prompt: {str(e)}",
                "operation": operation,
                "status": "FAILED"
            }
            log_agent(self.name, input_data, result)
            return result
        
        # Exécuter l'opération demandée
        try:
            if operation == "analyze":
                # Analyser les logs pour détecter des anomalies ou tendances
                logs = self._gather_logs(target_agent, time_period)
                
                # Construire le prompt pour l'analyse
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{time_period}}", time_period)
                prompt = prompt.replace("{{logs}}", json.dumps(logs, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour l'analyse
                analysis = ask_gpt_4_1(prompt)
                
                # Enregistrer les résultats de l'analyse
                result["analysis"] = analysis
                result["anomalies"] = analysis.get("anomalies", [])
                result["patterns"] = analysis.get("patterns", [])
                result["agent_interactions"] = analysis.get("agent_interactions", {})
                result["status"] = "COMPLETED"
                
                # Enregistrer les anomalies détectées
                self._record_anomalies(analysis.get("anomalies", []), target_agent)
                
                # Générer un rapport d'analyse
                self._generate_analysis_report(analysis, target_agent, time_period)
            
            elif operation == "generate_report":
                # Générer un rapport détaillé des logs
                report_type = input_data.get("report_type", "daily")
                include_metrics = input_data.get("include_metrics", True)
                
                # Récupérer les logs et métriques
                logs = self._gather_logs(target_agent, time_period)
                metrics = self._gather_metrics(target_agent, time_period) if include_metrics else {}
                
                # Construire le prompt pour la génération du rapport
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{time_period}}", time_period)
                prompt = prompt.replace("{{report_type}}", report_type)
                prompt = prompt.replace("{{logs}}", json.dumps(logs, ensure_ascii=False))
                prompt = prompt.replace("{{metrics}}", json.dumps(metrics, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour la génération du rapport
                report = ask_gpt_4_1(prompt)
                
                # Enregistrer le rapport
                report_path = self._save_report(report, target_agent, report_type)
                
                # Préparer le résultat
                result["report"] = report
                result["report_path"] = report_path
                result["charts"] = report.get("charts", [])
                result["summary"] = report.get("summary", "")
                result["status"] = "COMPLETED"
            
            elif operation == "detect_inconsistencies":
                # Détecter des incohérences dans les logs (ex: lead froid exporté)
                logs = self._gather_logs(target_agent, time_period)
                
                # Construire le prompt pour la détection d'incohérences
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{time_period}}", time_period)
                prompt = prompt.replace("{{logs}}", json.dumps(logs, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour la détection d'incohérences
                inconsistencies = ask_gpt_4_1(prompt)
                
                # Enregistrer les résultats
                result["inconsistencies"] = inconsistencies.get("inconsistencies", [])
                result["explanations"] = inconsistencies.get("explanations", [])
                result["recommendations"] = inconsistencies.get("recommendations", [])
                result["status"] = "COMPLETED"
                
                # Enregistrer les incohérences détectées
                self._record_inconsistencies(inconsistencies, target_agent)
            
            elif operation == "inject_memory":
                # Injecter les insights des logs dans la mémoire (via MemoryManager)
                insights = input_data.get("insights", [])
                
                if not insights:
                    # Si aucun insight n'est fourni, en extraire des logs
                    logs = self._gather_logs(target_agent, time_period)
                    
                    # Construire le prompt pour l'extraction d'insights
                    prompt = prompt_template.replace("{{operation}}", "extract_insights")
                    prompt = prompt.replace("{{target_agent}}", target_agent)
                    prompt = prompt.replace("{{time_period}}", time_period)
                    prompt = prompt.replace("{{logs}}", json.dumps(logs, ensure_ascii=False))
                    
                    # Appeler GPT-4.1 pour l'extraction d'insights
                    extraction = ask_gpt_4_1(prompt)
                    insights = extraction.get("insights", [])
                
                # Préparer les insights pour l'injection dans la mémoire
                memory_data = {
                    "knowledge_points": insights,
                    "source": "agent_logs",
                    "target_collection": "campaign_knowledge"
                }
                
                # Enregistrer les résultats
                result["insights"] = insights
                result["memory_data"] = memory_data
                result["status"] = "COMPLETED"
                
                # Note: Dans une implémentation réelle, on appellerait le MemoryManagerAgent
                # pour injecter effectivement ces insights dans la mémoire vectorielle
            
            else:
                result = {
                    "error": f"Opération non reconnue: {operation}",
                    "operation": operation,
                    "status": "FAILED"
                }
                log_agent(self.name, input_data, result)
                return result
        
        except Exception as e:
            result = {
                "error": f"Erreur lors de l'exécution de l'opération: {str(e)}",
                "operation": operation,
                "status": "FAILED"
            }
            log_agent(self.name, input_data, result)
            return result
        
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _gather_logs(self, target_agent, time_period):
        """
        Récupère les logs selon l'agent ciblé et la période
        """
        logs = {}
        
        try:
            # Calculer la date limite selon la période
            now = datetime.datetime.now()
            
            if time_period == "today":
                limit_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "yesterday":
                limit_date = (now - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "week":
                limit_date = (now - datetime.timedelta(days=7))
            elif time_period == "month":
                limit_date = (now - datetime.timedelta(days=30))
            else:
                # Par défaut, prendre aujourd'hui
                limit_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Lister les fichiers de log dans le répertoire des logs
            log_files = [f for f in os.listdir(self.logs_dir) if f.endswith(".log")]
            
            # Filtrer par agent si spécifié
            if target_agent != "all":
                log_files = [f for f in log_files if f.startswith(f"{target_agent}_")]
            
            # Lire le contenu des fichiers de log et filtrer par date
            for log_file in log_files:
                agent_name = log_file.split("_")[0]
                
                if agent_name not in logs:
                    logs[agent_name] = []
                
                with open(f"{self.logs_dir}/{log_file}", "r") as f:
                    for line in f:
                        try:
                            # Essayer de parser la ligne et extraire la date
                            log_entry = json.loads(line)
                            log_timestamp = log_entry.get("timestamp")
                            
                            if log_timestamp:
                                log_date = datetime.datetime.fromisoformat(log_timestamp)
                                
                                # Ne garder que les logs après la date limite
                                if log_date >= limit_date:
                                    logs[agent_name].append(log_entry)
                        except Exception:
                            # Si la ligne n'est pas au format JSON, l'ignorer
                            continue
            
            return logs
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la récupération des logs: {str(e)}")
            return {}
    
    def _gather_metrics(self, target_agent, time_period):
        """
        Récupère les métriques de performance selon l'agent ciblé et la période
        """
        # Dans une implémentation réelle, on extrairait des métriques des logs
        # ou d'une base de données dédiée aux métriques
        
        # Pour l'instant, on simule des métriques basiques
        metrics = {
            "global": {
                "success_rate": 87.5,
                "error_rate": 12.5,
                "average_execution_time": 2.3  # secondes
            },
            "agents": {}
        }
        
        # Simuler des métriques par agent
        agent_list = ["StrategyAgent", "PlanningAgent", "AnalyticsAgent", "CleanerAgent", "LeadClassifierAgent"]
        
        if target_agent != "all":
            agent_list = [a for a in agent_list if a == target_agent]
        
        for agent in agent_list:
            # Simuler des métriques aléatoires (dans une implémentation réelle, ces valeurs seraient calculées)
            import random
            
            metrics["agents"][agent] = {
                "success_rate": random.uniform(75.0, 99.0),
                "error_rate": random.uniform(1.0, 25.0),
                "average_execution_time": random.uniform(0.5, 5.0),
                "calls_count": random.randint(10, 100)
            }
        
        return metrics
    
    def _record_anomalies(self, anomalies, target_agent):
        """
        Enregistre les anomalies détectées pour référence future
        """
        if not anomalies:
            return
        
        try:
            # Charger les anomalies existantes
            with open(self.anomalies_file, "r") as f:
                all_anomalies = json.load(f)
            
            # Ajouter les nouvelles anomalies
            for anomaly in anomalies:
                anomaly_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "agent": target_agent,
                    "description": anomaly.get("description", ""),
                    "severity": anomaly.get("severity", "medium"),
                    "context": anomaly.get("context", {}),
                    "resolved": False
                }
                
                all_anomalies["anomalies"].append(anomaly_entry)
            
            all_anomalies["last_updated"] = datetime.datetime.now().isoformat()
            
            # Sauvegarder les anomalies mises à jour
            with open(self.anomalies_file, "w") as f:
                json.dump(all_anomalies, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'enregistrement des anomalies: {str(e)}")
            return False
    
    def _record_inconsistencies(self, inconsistencies, target_agent):
        """
        Enregistre les incohérences détectées pour référence future
        """
        inconsistencies_list = inconsistencies.get("inconsistencies", [])
        
        if not inconsistencies_list:
            return
        
        try:
            # Enregistrer les incohérences dans un fichier dédié
            filename = f"{self.reports_dir}/inconsistencies_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            
            with open(filename, "w") as f:
                json.dump({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "agent": target_agent,
                    "inconsistencies": inconsistencies_list,
                    "explanations": inconsistencies.get("explanations", []),
                    "recommendations": inconsistencies.get("recommendations", [])
                }, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'enregistrement des incohérences: {str(e)}")
            return False
    
    def _generate_analysis_report(self, analysis, target_agent, time_period):
        """
        Génère un rapport d'analyse basé sur les résultats
        """
        try:
            # Préparer le rapport
            report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "target_agent": target_agent,
                "time_period": time_period,
                "anomalies": analysis.get("anomalies", []),
                "patterns": analysis.get("patterns", []),
                "agent_interactions": analysis.get("agent_interactions", {}),
                "recommendations": analysis.get("recommendations", [])
            }
            
            # Enregistrer le rapport
            filename = f"{self.reports_dir}/analysis_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            
            return filename
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la génération du rapport: {str(e)}")
            return None
    
    def _save_report(self, report, target_agent, report_type):
        """
        Sauvegarde un rapport généré
        """
        try:
            # Déterminer le nom du fichier selon le type de rapport
            if report_type == "daily":
                filename = f"{self.reports_dir}/daily_report_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            elif report_type == "weekly":
                filename = f"{self.reports_dir}/weekly_report_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            elif report_type == "monthly":
                filename = f"{self.reports_dir}/monthly_report_{target_agent}_{datetime.datetime.now().strftime('%Y%m')}.json"
            else:
                filename = f"{self.reports_dir}/report_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            
            # Enregistrer le rapport
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            
            return filename
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde du rapport: {str(e)}")
            return None
    
    def daily_summary(self):
        """
        Génère un résumé quotidien de l'activité des agents
        """
        try:
            # Exécuter une analyse pour la journée
            input_data = {
                "operation": "generate_report",
                "target_agent": "all",
                "time_period": "today",
                "report_type": "daily",
                "include_metrics": True
            }
            
            result = self.run(input_data)
            
            # Vérifier si le rapport a été généré avec succès
            if result.get("status") == "COMPLETED" and "report_path" in result:
                print(f"[{self.name}] ✅ Résumé quotidien généré: {result['report_path']}")
                
                # Dans une implémentation réelle, on pourrait envoyer une notification
                # ou publier le rapport sur un tableau de bord
                
                return result
            else:
                print(f"[{self.name}] ⚠️ Erreur lors de la génération du résumé quotidien")
                return {"error": "Échec de la génération du résumé", "status": "FAILED"}
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la génération du résumé quotidien: {str(e)}")
            return {"error": str(e), "status": "FAILED"}
    
    def detect_system_drift(self):
        """
        Détecte les dérives du système en analysant les logs sur une période longue
        """
        try:
            # Exécuter une analyse sur le mois
            input_data = {
                "operation": "analyze",
                "target_agent": "all",
                "time_period": "month"
            }
            
            result = self.run(input_data)
            
            # Si des anomalies sont détectées, les enregistrer
            if result.get("status") == "COMPLETED" and result.get("anomalies"):
                print(f"[{self.name}] 🔍 Dérives système détectées: {len(result['anomalies'])}")
                
                # Si des dérives significatives sont détectées, on pourrait déclencher une alerte
                severe_anomalies = [a for a in result.get("anomalies", []) if a.get("severity") == "high"]
                
                if severe_anomalies:
                    print(f"[{self.name}] ⚠️ ALERTE: {len(severe_anomalies)} anomalies sévères détectées")
                    # Dans une implémentation réelle, envoyer une alerte
                
                return result
            else:
                print(f"[{self.name}] ✅ Aucune dérive système significative détectée")
                return {"message": "Aucune dérive significative", "status": "COMPLETED"}
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la détection de dérives: {str(e)}")
            return {"error": str(e), "status": "FAILED"}
