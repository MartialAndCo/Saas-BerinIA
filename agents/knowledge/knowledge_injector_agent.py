from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
from memory.qdrant import QdrantClient
import json
import datetime
import os
import re

class KnowledgeInjectorAgent(AgentBase):
    def __init__(self):
        super().__init__("KnowledgeInjectorAgent")
        self.prompt_path = "prompts/knowledge_injector_agent_prompt.txt"
        self.qdrant_client = QdrantClient()
        self.prompts_dir = "prompts"
        self.logs_dir = "logs"
        self.agent_performance_file = "logs/agent_performance.json"
        self.prompt_tests_file = "logs/prompt_tests.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensures that necessary files for knowledge injection exist"""
        # Agent performance tracking file
        if not os.path.exists(self.agent_performance_file):
            initial_data = {
                "agents": {},
                "global_metrics": {
                    "success_rate": 0,
                    "error_rate": 0,
                    "average_execution_time": 0
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.agent_performance_file, "w") as f:
                json.dump(initial_data, f, indent=2)
        
        # Prompt tests tracking file
        if not os.path.exists(self.prompt_tests_file):
            initial_tests = {
                "test_results": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.prompt_tests_file, "w") as f:
                json.dump(initial_tests, f, indent=2)

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 📚 Analyse et injection de connaissances...")
        
        # Extraire les paramètres d'entrée
        operation = input_data.get("operation", "analyze")
        target_agent = input_data.get("target_agent", "all")
        knowledge_source = input_data.get("source", "logs")
        collection_name = input_data.get("collection", "campaign_knowledge")
        
        # Préparer le résultat
        result = {
            "operation": operation,
            "target_agent": target_agent,
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
        
        # Récupérer les données nécessaires selon l'opération
        try:
            if operation == "analyze":
                # Analyser les logs et performances des agents
                agent_logs = self._gather_agent_logs(target_agent)
                agent_performance = self._load_agent_performance()
                
                # Construire le prompt pour l'analyse
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{agent_logs}}", json.dumps(agent_logs, ensure_ascii=False))
                prompt = prompt.replace("{{agent_performance}}", json.dumps(agent_performance, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour l'analyse
                analysis = ask_gpt_4_1(prompt)
                
                # Enregistrer les résultats de l'analyse
                result["analysis"] = analysis
                result["knowledge_gaps"] = analysis.get("knowledge_gaps", [])
                result["improvement_suggestions"] = analysis.get("improvement_suggestions", [])
                result["status"] = "COMPLETED"
            
            elif operation == "inject":
                # Injecter de nouvelles connaissances
                knowledge_data = input_data.get("knowledge_data", {})
                
                if not knowledge_data and knowledge_source == "logs":
                    # Analyser d'abord les logs pour identifier des connaissances à injecter
                    agent_logs = self._gather_agent_logs(target_agent)
                    agent_performance = self._load_agent_performance()
                    
                    # Construire le prompt pour extraire des connaissances
                    prompt = prompt_template.replace("{{operation}}", "extract")
                    prompt = prompt.replace("{{target_agent}}", target_agent)
                    prompt = prompt.replace("{{agent_logs}}", json.dumps(agent_logs, ensure_ascii=False))
                    prompt = prompt.replace("{{agent_performance}}", json.dumps(agent_performance, ensure_ascii=False))
                    
                    # Appeler GPT-4.1 pour extraire des connaissances
                    extraction = ask_gpt_4_1(prompt)
                    knowledge_data = extraction.get("extracted_knowledge", {})
                
                # Maintenant, injecter les connaissances dans la mémoire vectorielle
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{knowledge_data}}", json.dumps(knowledge_data, ensure_ascii=False))
                prompt = prompt.replace("{{collection_name}}", collection_name)
                
                # Appeler GPT-4.1 pour formater les connaissances
                injection_data = ask_gpt_4_1(prompt)
                
                # Injecter les connaissances dans Qdrant
                injection_result = self._inject_knowledge(injection_data, collection_name)
                
                # Enregistrer les résultats de l'injection
                result.update(injection_result)
                result["status"] = "COMPLETED"
            
            elif operation == "verify_prompts":
                # Vérifier la cohérence et la qualité des prompts
                prompts = self._gather_prompts(target_agent)
                
                # Construire le prompt pour la vérification
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{prompts}}", json.dumps(prompts, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour la vérification
                verification = ask_gpt_4_1(prompt)
                
                # Enregistrer les résultats de la vérification
                result["verification"] = verification
                result["prompt_issues"] = verification.get("prompt_issues", [])
                result["improvement_suggestions"] = verification.get("improvement_suggestions", [])
                result["status"] = "COMPLETED"
                
                # Sauvegarder les suggestions d'amélioration pour référence future
                self._save_prompt_improvement_suggestions(target_agent, verification)
            
            elif operation == "test_prompt":
                # Tester une nouvelle version de prompt
                original_prompt = input_data.get("original_prompt", "")
                new_prompt = input_data.get("new_prompt", "")
                test_cases = input_data.get("test_cases", [])
                
                if not original_prompt or not new_prompt:
                    # Récupérer le prompt existant si non fourni
                    agent_name = target_agent
                    prompt_path = f"{self.prompts_dir}/{agent_name}_prompt.txt"
                    
                    if os.path.exists(prompt_path):
                        with open(prompt_path, "r") as f:
                            original_prompt = f.read()
                    
                    if not new_prompt and "prompt_suggestion" in input_data:
                        new_prompt = input_data["prompt_suggestion"]
                
                if not test_cases:
                    # Générer des cas de test automatiquement
                    test_prompt = prompt_template.replace("{{operation}}", "generate_tests")
                    test_prompt = test_prompt.replace("{{target_agent}}", target_agent)
                    test_prompt = test_prompt.replace("{{original_prompt}}", original_prompt)
                    
                    # Appeler GPT-4.1 pour générer des cas de test
                    test_generation = ask_gpt_4_1(test_prompt)
                    test_cases = test_generation.get("test_cases", [])
                
                # Construire le prompt pour le test
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt_template.replace("{{target_agent}}", target_agent)
                prompt = prompt.replace("{{original_prompt}}", original_prompt)
                prompt = prompt.replace("{{new_prompt}}", new_prompt)
                prompt = prompt.replace("{{test_cases}}", json.dumps(test_cases, ensure_ascii=False))
                
                # Appeler GPT-4.1 pour le test
                test_results = ask_gpt_4_1(prompt)
                
                # Enregistrer les résultats du test
                result["test_results"] = test_results
                result["comparison"] = test_results.get("comparison", {})
                result["recommendation"] = test_results.get("recommendation", "")
                result["status"] = "COMPLETED"
                
                # Sauvegarder les résultats du test pour référence future
                self._save_prompt_test_results(target_agent, original_prompt, new_prompt, test_results)
            
            elif operation == "update_prompt":
                # Mettre à jour le prompt d'un agent
                new_prompt = input_data.get("new_prompt", "")
                reason = input_data.get("reason", "Amélioration manuelle")
                
                if not new_prompt:
                    result = {
                        "error": "Aucun nouveau prompt fourni",
                        "operation": operation,
                        "status": "FAILED"
                    }
                    log_agent(self.name, input_data, result)
                    return result
                
                # Sauvegarder l'ancien prompt pour référence
                agent_name = target_agent
                prompt_path = f"{self.prompts_dir}/{agent_name}_prompt.txt"
                backup_path = f"{self.prompts_dir}/{agent_name}_prompt_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                
                if os.path.exists(prompt_path):
                    with open(prompt_path, "r") as f:
                        old_prompt = f.read()
                    
                    with open(backup_path, "w") as f:
                        f.write(old_prompt)
                
                # Écrire le nouveau prompt
                with open(prompt_path, "w") as f:
                    f.write(new_prompt)
                
                # Enregistrer les résultats de la mise à jour
                result["updated"] = True
                result["backup_path"] = backup_path
                result["reason"] = reason
                result["status"] = "COMPLETED"
                
                # Enregistrer la mise à jour dans les logs
                update_log = {
                    "agent": agent_name,
                    "operation": "prompt_update",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "reason": reason,
                    "backup_path": backup_path
                }
                
                with open(f"{self.logs_dir}/prompt_updates.log", "a") as f:
                    f.write(json.dumps(update_log) + "\n")
            
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
    
    def _gather_agent_logs(self, target_agent):
        """
        Récupère les logs des agents ciblés
        """
        logs = {}
        
        try:
            # Lister les fichiers de log dans le répertoire des logs
            log_files = [f for f in os.listdir(self.logs_dir) if f.endswith(".log")]
            
            # Filtrer par agent si spécifié
            if target_agent != "all":
                log_files = [f for f in log_files if f.startswith(f"{target_agent}_")]
            
            # Limiter le nombre de fichiers pour éviter de surcharger le prompt
            log_files = sorted(log_files, reverse=True)[:10]  # Prendre les 10 plus récents
            
            # Lire le contenu des fichiers de log
            for log_file in log_files:
                agent_name = log_file.split("_")[0]
                
                if agent_name not in logs:
                    logs[agent_name] = []
                
                with open(f"{self.logs_dir}/{log_file}", "r") as f:
                    # Lire les dernières lignes (jusqu'à 100) pour chaque fichier
                    lines = f.readlines()[-100:] if len(f.readlines()) > 100 else f.readlines()
                    logs[agent_name].extend(lines)
            
            return logs
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la récupération des logs: {str(e)}")
            return {}
    
    def _load_agent_performance(self):
        """
        Charge les données de performance des agents
        """
        try:
            with open(self.agent_performance_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des performances: {str(e)}")
            return {"agents": {}, "global_metrics": {}}
    
    def _gather_prompts(self, target_agent):
        """
        Récupère les prompts des agents ciblés
        """
        prompts = {}
        
        try:
            # Lister les fichiers de prompt dans le répertoire des prompts
            prompt_files = [f for f in os.listdir(self.prompts_dir) if f.endswith("_prompt.txt")]
            
            # Filtrer par agent si spécifié
            if target_agent != "all":
                prompt_files = [f for f in prompt_files if f.startswith(f"{target_agent}_prompt.txt")]
            
            # Lire le contenu des fichiers de prompt
            for prompt_file in prompt_files:
                agent_name = prompt_file.replace("_prompt.txt", "")
                
                with open(f"{self.prompts_dir}/{prompt_file}", "r") as f:
                    prompts[agent_name] = f.read()
            
            return prompts
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la récupération des prompts: {str(e)}")
            return {}
    
    def _inject_knowledge(self, injection_data, collection_name):
        """
        Injecte des connaissances dans la mémoire vectorielle
        """
        result = {
            "injected_count": 0,
            "knowledge_ids": [],
            "collection_name": collection_name
        }
        
        try:
            # Extraire les connaissances à injecter
            knowledge_points = injection_data.get("knowledge_points", [])
            
            if not knowledge_points:
                return {
                    "error": "Aucune connaissance à injecter",
                    "injected_count": 0
                }
            
            # Préparer les points pour Qdrant
            vectors = []
            for point in knowledge_points:
                # Dans une implémentation réelle, on vectoriserait le contenu
                # Pour l'instant, on simule simplement le processus
                vectors.append({
                    "content": point.get("content", ""),
                    "metadata": {
                        "source": point.get("source", "unknown"),
                        "agent": point.get("agent", "unknown"),
                        "confidence": point.get("confidence", 0.8),
                        "tags": point.get("tags", []),
                        "created_at": datetime.datetime.now().isoformat()
                    }
                })
            
            # Injecter dans Qdrant
            upload_result = self.qdrant_client.upload_points(collection_name, vectors)
            
            # Générer des IDs factices pour la démonstration
            knowledge_ids = [f"knowledge_{i}_{int(datetime.datetime.now().timestamp())}" for i in range(len(vectors))]
            
            result["injected_count"] = len(vectors)
            result["knowledge_ids"] = knowledge_ids
            
            return result
        
        except Exception as e:
            return {
                "error": f"Erreur lors de l'injection de connaissances: {str(e)}",
                "injected_count": 0
            }
    
    def _save_prompt_improvement_suggestions(self, agent_name, verification_results):
        """
        Sauvegarde les suggestions d'amélioration de prompt pour référence future
        """
        try:
            suggestions_log = {
                "agent": agent_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "issues": verification_results.get("prompt_issues", []),
                "suggestions": verification_results.get("improvement_suggestions", [])
            }
            
            with open(f"{self.logs_dir}/prompt_suggestions_{agent_name}_{datetime.datetime.now().strftime('%Y%m%d')}.json", "w") as f:
                json.dump(suggestions_log, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde des suggestions: {str(e)}")
            return False
    
    def _save_prompt_test_results(self, agent_name, original_prompt, new_prompt, test_results):
        """
        Sauvegarde les résultats de test de prompt pour référence future
        """
        try:
            # Charger les tests existants
            with open(self.prompt_tests_file, "r") as f:
                all_tests = json.load(f)
            
            # Ajouter le nouveau test
            test_entry = {
                "agent": agent_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "original_prompt_excerpt": self._get_prompt_excerpt(original_prompt),
                "new_prompt_excerpt": self._get_prompt_excerpt(new_prompt),
                "comparison": test_results.get("comparison", {}),
                "recommendation": test_results.get("recommendation", ""),
                "approved": False  # À approuver manuellement
            }
            
            all_tests["test_results"].append(test_entry)
            all_tests["last_updated"] = datetime.datetime.now().isoformat()
            
            # Sauvegarder les tests mis à jour
            with open(self.prompt_tests_file, "w") as f:
                json.dump(all_tests, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde des résultats de test: {str(e)}")
            return False
    
    def _get_prompt_excerpt(self, prompt, max_length=200):
        """
        Récupère un extrait du prompt pour l'affichage
        """
        if not prompt:
            return ""
        
        # Nettoyer le prompt (enlever les espaces multiples)
        cleaned_prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        # Tronquer si nécessaire
        if len(cleaned_prompt) > max_length:
            return cleaned_prompt[:max_length] + "..."
        else:
            return cleaned_prompt
    
    def identify_agent_gaps(self):
        """
        Identifie les lacunes des agents basé sur leurs logs et performances
        """
        try:
            # Récupérer les données nécessaires
            agent_logs = self._gather_agent_logs("all")
            agent_performance = self._load_agent_performance()
            
            # Préparer le prompt pour l'analyse
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
            
            prompt = prompt_template.replace("{{operation}}", "identify_gaps")
            prompt = prompt.replace("{{target_agent}}", "all")
            prompt = prompt.replace("{{agent_logs}}", json.dumps(agent_logs))
            prompt = prompt.replace("{{agent_performance}}", json.dumps(agent_performance))
            
            # Appeler GPT-4.1 pour l'analyse
            gap_analysis = ask_gpt_4_1(prompt)
            
            # Enregistrer les résultats
            with open(f"{self.logs_dir}/agent_gaps_{datetime.datetime.now().strftime('%Y%m%d')}.json", "w") as f:
                json.dump(gap_analysis, f, indent=2)
            
            return gap_analysis
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'identification des lacunes: {str(e)}")
            return {"error": str(e)}
    
    def launch_test_campaign(self, test_config):
        """
        Lance une campagne de test avec des prompts modifiés
        """
        try:
            # Extraire la configuration de test
            target_agent = test_config.get("agent", "")
            prompt_variations = test_config.get("prompt_variations", [])
            test_cases = test_config.get("test_cases", [])
            
            if not target_agent or not prompt_variations:
                return {
                    "error": "Configuration de test incomplète",
                    "status": "FAILED"
                }
            
            # Récupérer le prompt original
            original_prompt = ""
            prompt_path = f"{self.prompts_dir}/{target_agent}_prompt.txt"
            
            if os.path.exists(prompt_path):
                with open(prompt_path, "r") as f:
                    original_prompt = f.read()
            
            # Exécuter les tests pour chaque variation
            test_results = []
            
            for i, variation in enumerate(prompt_variations):
                # Préparer les données d'entrée pour le test
                test_input = {
                    "operation": "test_prompt",
                    "target_agent": target_agent,
                    "original_prompt": original_prompt,
                    "new_prompt": variation.get("prompt", ""),
                    "test_cases": test_cases,
                    "variation_name": variation.get("name", f"Variation {i+1}")
                }
                
                # Exécuter le test
                result = self.run(test_input)
                
                # Ajouter aux résultats
                test_results.append({
                    "variation_name": variation.get("name", f"Variation {i+1}"),
                    "results": result.get("test_results", {}),
                    "recommendation": result.get("recommendation", "")
                })
            
            # Analyser les résultats pour déterminer la meilleure variation
            best_variation = self._find_best_prompt_variation(test_results)
            
            # Enregistrer les résultats complets
            campaign_results = {
                "agent": target_agent,
                "timestamp": datetime.datetime.now().isoformat(),
                "original_prompt_excerpt": self._get_prompt_excerpt(original_prompt),
                "test_count": len(prompt_variations),
                "results": test_results,
                "best_variation": best_variation
            }
            
            with open(f"{self.logs_dir}/test_campaign_{target_agent}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
                json.dump(campaign_results, f, indent=2)
            
            return campaign_results
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la campagne de test: {str(e)}")
            return {"error": str(e), "status": "FAILED"}
    
    def _find_best_prompt_variation(self, test_results):
        """
        Détermine la meilleure variation de prompt basée sur les résultats de test
        """
        best_variation = None
        best_score = -1
        
        for result in test_results:
            comparison = result.get("results", {}).get("comparison", {})
            
            # Calculer un score simplifié
            score = 0
            
            if "accuracy" in comparison:
                score += comparison["accuracy"] * 0.5
            
            if "clarity" in comparison:
                score += comparison["clarity"] * 0.3
            
            if "efficiency" in comparison:
                score += comparison["efficiency"] * 0.2
            
            if score > best_score:
                best_score = score
                best_variation = {
                    "name": result.get("variation_name", ""),
                    "score": score,
                    "improvement": comparison.get("improvement", 0),
                    "recommendation": result.get("recommendation", "")
                }
        
        return best_variation
