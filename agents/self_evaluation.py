from datetime import datetime
import time
import json
from typing import Dict, Any, List, Optional
import logging
import numpy as np

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class SelfEvaluationAgent(BaseAgent):
    """
    Agent responsable de l'auto-évaluation des performances des autres agents.
    
    Cet agent analyse les logs d'exécution des autres agents et fournit des
    évaluations objectives de leur performance selon différents critères.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
    
    def run(self, input_data=None):
        """
        Exécute l'agent d'auto-évaluation.
        
        Args:
            input_data (dict, optional): Les données d'entrée, qui peuvent inclure:
                - agent_ids: Liste des IDs d'agents à évaluer (si vide, tous les agents)
                - log_ids: Liste des IDs de logs spécifiques à évaluer
                - criteria: Critères d'évaluation spécifiques
                - start_date: Date de début pour la période d'évaluation
                - end_date: Date de fin pour la période d'évaluation
                - limit: Nombre maximal de logs à évaluer
                
        Returns:
            dict: Résultats de l'évaluation
        """
        self.logger.info("Lancement de SelfEvaluationAgent")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            agent_ids = input_data.get('agent_ids', []) if input_data else []
            log_ids = input_data.get('log_ids', []) if input_data else []
            criteria = input_data.get('criteria', {}) if input_data else {}
            start_date = input_data.get('start_date') if input_data else None
            end_date = input_data.get('end_date') if input_data else None
            limit = input_data.get('limit', 100) if input_data else 100
            
            # Par défaut, évaluer les logs récents sans feedback
            logs_to_evaluate = self._get_logs_to_evaluate(
                agent_ids=agent_ids,
                log_ids=log_ids,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            self.logger.info(f"Évaluation de {len(logs_to_evaluate)} logs")
            
            # Évaluer chaque log
            evaluation_results = []
            for log in logs_to_evaluate:
                evaluation = self.evaluate_log(log, criteria)
                evaluation_results.append(evaluation)
                
                # Pause pour éviter de surcharger l'API LLM
                time.sleep(0.5)
            
            # Calculer des statistiques d'évaluation globales
            statistics = self._calculate_statistics(evaluation_results)
            
            execution_time = time.time() - start_time
            
            # Préparer les résultats
            results = {
                'evaluated_logs': len(evaluation_results),
                'results': evaluation_results,
                'statistics': statistics,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation="evaluate_agents",
                input_data=input_data if input_data else {},
                output_data={
                    'evaluated_logs': len(evaluation_results),
                    'average_score': statistics.get('average_score', 0)
                },
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de SelfEvaluationAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="evaluate_agents",
                input_data=input_data if input_data else {},
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {
                'status': 'error',
                'message': str(e),
                'evaluated_logs': 0
            }
    
    def _get_logs_to_evaluate(self, agent_ids=None, log_ids=None, start_date=None, end_date=None, limit=100):
        """
        Récupère les logs à évaluer selon les critères.
        
        Args:
            agent_ids: Liste des IDs d'agents
            log_ids: Liste des IDs de logs spécifiques
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre maximal de logs
            
        Returns:
            list: Liste des logs à évaluer
        """
        try:
            # Construire la requête
            query = self.db.query(AgentLog).filter(
                AgentLog.status == "completed",
                AgentLog.feedback_score.is_(None)  # Logs sans feedback existant
            )
            
            # Filtrer par IDs d'agents
            if agent_ids:
                query = query.filter(AgentLog.agent_id.in_(agent_ids))
            
            # Filtrer par IDs de logs
            if log_ids:
                query = query.filter(AgentLog.id.in_(log_ids))
            
            # Filtrer par date
            if start_date:
                query = query.filter(AgentLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AgentLog.timestamp <= end_date)
            
            # Ordonner et limiter
            logs = query.order_by(AgentLog.timestamp.desc()).limit(limit).all()
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des logs: {str(e)}")
            return []
    
    def evaluate_log(self, log, criteria=None):
        """
        Évalue un log d'agent selon plusieurs critères.
        
        Args:
            log: Log d'agent à évaluer
            criteria: Critères d'évaluation personnalisés
            
        Returns:
            dict: Résultat de l'évaluation
        """
        # Récupérer l'agent concerné
        agent = self.db.query(AgentModel).filter(AgentModel.id == log.agent_id).first()
        
        if not agent:
            return {
                'log_id': log.id,
                'agent_id': log.agent_id,
                'error': "Agent non trouvé"
            }
        
        # Critères d'évaluation par défaut
        default_criteria = {
            "accuracy": self._evaluate_accuracy,
            "efficiency": self._evaluate_efficiency,
            "usefulness": self._evaluate_usefulness,
            "quality": self._evaluate_quality
        }
        
        # Utiliser les critères personnalisés s'ils sont fournis
        evaluation_criteria = criteria if criteria else default_criteria
        
        # Évaluer selon chaque critère
        criteria_results = {}
        for criterion_name, criterion_method in evaluation_criteria.items():
            if callable(criterion_method):
                criteria_results[criterion_name] = criterion_method(log, agent)
            else:
                # Si c'est un dictionnaire de configuration plutôt qu'une méthode
                method_name = f"_evaluate_{criterion_name}"
                if hasattr(self, method_name) and callable(getattr(self, method_name)):
                    method = getattr(self, method_name)
                    criteria_results[criterion_name] = method(log, agent, config=criterion_method)
        
        # Calculer le score global
        if criteria_results:
            score = sum(criteria_results.values()) / len(criteria_results)
        else:
            score = 0.0
        
        # Générer un feedback textuel
        feedback_text = self._generate_feedback_text(log, agent, criteria_results)
        
        # Enregistrer l'évaluation dans la base de données
        self._save_evaluation(log.id, score, criteria_results, feedback_text)
        
        # Préparer le résultat
        evaluation = {
            'log_id': log.id,
            'agent_id': log.agent_id,
            'agent_name': agent.name,
            'operation': log.operation,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
            'score': score,
            'criteria': criteria_results,
            'feedback': feedback_text,
            'evaluated_at': datetime.utcnow().isoformat()
        }
        
        return evaluation
    
    def _evaluate_accuracy(self, log, agent, config=None):
        """
        Évalue la précision du résultat de l'agent.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            config: Configuration spécifique
            
        Returns:
            float: Score de précision (0.0-1.0)
        """
        # Valeur par défaut
        default_score = 0.5
        
        # Si le log n'a pas de output_data, retourner une valeur par défaut
        if not log.output_data:
            return default_score
        
        try:
            # Charger les données d'entrée et de sortie
            input_data = log.input_data if isinstance(log.input_data, dict) else json.loads(log.input_data or '{}')
            output_data = log.output_data if isinstance(log.output_data, dict) else json.loads(log.output_data or '{}')
            
            # Détecter les erreurs évidentes
            if 'error' in output_data or log.status == 'error':
                return 0.0
            
            # Analyser selon le type d'opération
            operation = log.operation
            
            # Cas spécifiques selon l'opération
            if 'analyze' in operation:
                # Pour les opérations d'analyse, vérifier la complétude et la structure
                if 'analysis' in output_data and isinstance(output_data['analysis'], dict):
                    # Vérifier la présence de champs clés attendus
                    expected_keys = ['summary', 'detailed']
                    present_keys = [k for k in expected_keys if k in output_data['analysis']]
                    return len(present_keys) / len(expected_keys)
                
            elif 'classify' in operation:
                # Pour les opérations de classification, vérifier la présence de scores et catégories
                if 'classified_leads' in output_data and isinstance(output_data['classified_leads'], list):
                    if not output_data['classified_leads']:
                        return 0.5  # Aucun lead classifié, résultat neutre
                    
                    # Vérifier que chaque lead a un score et une catégorie
                    valid_leads = 0
                    for lead in output_data['classified_leads']:
                        if 'score' in lead and 'category' in lead:
                            valid_leads += 1
                    
                    return valid_leads / len(output_data['classified_leads'])
                
            elif 'send_messages' in operation:
                # Pour les opérations d'envoi de messages, vérifier le taux de succès
                if 'messages_sent' in output_data and 'messages_failed' in output_data:
                    total = output_data['messages_sent'] + output_data['messages_failed']
                    if total > 0:
                        return output_data['messages_sent'] / total
                    
            # Pour les autres opérations, évaluer la cohérence entre entrée et sortie
            # Cette partie nécessiterait une logique spécifique à chaque type d'agent
            
            # En l'absence d'heuristiques spécifiques, utiliser le LLM pour évaluer
            return self._llm_evaluate_accuracy(log, agent)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de la précision: {str(e)}")
            return default_score
    
    def _evaluate_efficiency(self, log, agent, config=None):
        """
        Évalue l'efficacité de l'exécution de l'agent.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            config: Configuration spécifique
            
        Returns:
            float: Score d'efficacité (0.0-1.0)
        """
        # Valeur par défaut
        default_score = 0.7
        
        # Si le temps d'exécution n'est pas disponible, retourner une valeur par défaut
        if log.execution_time is None:
            return default_score
        
        try:
            # Récupérer les temps d'exécution typiques pour cet agent et cette opération
            typical_times = self._get_typical_execution_times(agent.id, log.operation)
            
            if not typical_times:
                return default_score
            
            # Calculer des statistiques sur les temps typiques
            avg_time = np.mean(typical_times)
            std_dev = np.std(typical_times)
            
            # Si l'écart type est très petit, utiliser une valeur minimale
            if std_dev < 0.1:
                std_dev = 0.1
            
            # Calculer combien d'écarts types le temps actuel est par rapport à la moyenne
            z_score = (log.execution_time - avg_time) / std_dev
            
            # Convertir en score (plus le z-score est négatif, meilleur est le score)
            # Un z-score de -2 ou moins (beaucoup plus rapide) donne 1.0
            # Un z-score de 2 ou plus (beaucoup plus lent) donne 0.0
            if z_score <= -2:
                return 1.0
            elif z_score >= 2:
                return 0.0
            else:
                # Conversion linéaire entre -2 et 2
                return 0.5 - (z_score / 4)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de l'efficacité: {str(e)}")
            return default_score
    
    def _get_typical_execution_times(self, agent_id, operation):
        """
        Récupère les temps d'exécution typiques pour un agent et une opération.
        
        Args:
            agent_id: ID de l'agent
            operation: Type d'opération
            
        Returns:
            list: Liste des temps d'exécution
        """
        try:
            # Récupérer les 50 derniers logs réussis
            logs = self.db.query(AgentLog).filter(
                AgentLog.agent_id == agent_id,
                AgentLog.operation == operation,
                AgentLog.status == "completed",
                AgentLog.execution_time.isnot(None)
            ).order_by(AgentLog.timestamp.desc()).limit(50).all()
            
            # Extraire les temps d'exécution
            return [log.execution_time for log in logs]
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des temps d'exécution: {str(e)}")
            return []
    
    def _evaluate_usefulness(self, log, agent, config=None):
        """
        Évalue l'utilité du résultat produit par l'agent.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            config: Configuration spécifique
            
        Returns:
            float: Score d'utilité (0.0-1.0)
        """
        # Valeur par défaut
        default_score = 0.6
        
        try:
            # Charger les données de sortie
            output_data = log.output_data if isinstance(log.output_data, dict) else json.loads(log.output_data or '{}')
            
            # Vérifier si nous avons des feedbacks humains précédents pour des logs similaires
            similar_logs_with_feedback = self._find_similar_logs_with_feedback(log)
            
            if similar_logs_with_feedback:
                # Utiliser les feedbacks précédents comme référence
                feedback_scores = [l.feedback_score for l in similar_logs_with_feedback if l.feedback_score is not None]
                if feedback_scores:
                    return sum(feedback_scores) / len(feedback_scores)
            
            # Vérifier les indicateurs spécifiques selon le type d'agent
            agent_type = agent.type if hasattr(agent, 'type') else None
            
            if agent_type == 'analytics':
                # Pour les agents d'analyse, vérifier la présence de recommandations
                if 'recommendations' in output_data and isinstance(output_data['recommendations'], list):
                    if not output_data['recommendations']:
                        return 0.3  # Aucune recommandation
                    
                    # Plus il y a de recommandations pertinentes, mieux c'est
                    return min(1.0, len(output_data['recommendations']) * 0.2)
                
            elif agent_type == 'messenger':
                # Pour les agents de messagerie, vérifier le nombre de messages envoyés
                if 'messages_sent' in output_data:
                    # Un score proportionnel au nombre de messages, plafonné à 1.0
                    return min(1.0, output_data['messages_sent'] * 0.1)
                
            # En l'absence d'heuristiques spécifiques, utiliser le LLM pour évaluer
            return self._llm_evaluate_usefulness(log, agent)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de l'utilité: {str(e)}")
            return default_score
    
    def _evaluate_quality(self, log, agent, config=None):
        """
        Évalue la qualité globale du travail de l'agent.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            config: Configuration spécifique
            
        Returns:
            float: Score de qualité (0.0-1.0)
        """
        # Utiliser le LLM pour une évaluation globale de la qualité
        return self._llm_evaluate_quality(log, agent)
    
    def _find_similar_logs_with_feedback(self, log):
        """
        Trouve des logs similaires qui ont reçu un feedback humain.
        
        Args:
            log: Log à comparer
            
        Returns:
            list: Liste des logs similaires avec feedback
        """
        try:
            # Trouver des logs du même agent et pour la même opération
            similar_logs = self.db.query(AgentLog).filter(
                AgentLog.agent_id == log.agent_id,
                AgentLog.operation == log.operation,
                AgentLog.feedback_score.isnot(None),  # Avec feedback
                AgentLog.feedback_source == 'human'  # Feedback humain
            ).order_by(AgentLog.timestamp.desc()).limit(10).all()
            
            return similar_logs
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de logs similaires: {str(e)}")
            return []
    
    def _llm_evaluate_accuracy(self, log, agent):
        """
        Utilise un LLM pour évaluer la précision d'un résultat.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            
        Returns:
            float: Score de précision estimé (0.0-1.0)
        """
        try:
            # Charger les données d'entrée et de sortie
            input_data = log.input_data if isinstance(log.input_data, dict) else json.loads(log.input_data or '{}')
            output_data = log.output_data if isinstance(log.output_data, dict) else json.loads(log.output_data or '{}')
            
            # Préparer le prompt pour le LLM
            prompt = f"""
            Évalue la précision du résultat produit par cet agent:
            
            Agent: {agent.name}
            Opération: {log.operation}
            
            Données d'entrée:
            {json.dumps(input_data, indent=2)}
            
            Résultat produit:
            {json.dumps(output_data, indent=2)}
            
            Attribue un score de précision entre 0.0 et 1.0, où:
            - 1.0 signifie que le résultat est parfaitement précis et répond exactement à ce qui était demandé
            - 0.5 signifie que le résultat est partiellement précis ou contient des informations incomplètes
            - 0.0 signifie que le résultat est complètement imprécis ou erroné
            
            Justifie ton évaluation mais retourne uniquement un nombre entre 0.0 et 1.0.
            """
            
            # Obtenir la réponse du LLM
            response = ask_llm(prompt=prompt, max_tokens=50)
            
            # Extraire le score (chercher un nombre entre 0.0 et 1.0)
            text = response.get('text', '')
            import re
            score_match = re.search(r'(\d+\.\d+|\d+)', text)
            
            if score_match:
                score = float(score_match.group(1))
                # S'assurer que le score est dans la plage [0.0, 1.0]
                return max(0.0, min(1.0, score))
            else:
                # Valeur par défaut si aucun score n'est trouvé
                return 0.6
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation LLM de la précision: {str(e)}")
            return 0.5
    
    def _llm_evaluate_usefulness(self, log, agent):
        """
        Utilise un LLM pour évaluer l'utilité d'un résultat.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            
        Returns:
            float: Score d'utilité estimé (0.0-1.0)
        """
        try:
            # Charger les données d'entrée et de sortie
            input_data = log.input_data if isinstance(log.input_data, dict) else json.loads(log.input_data or '{}')
            output_data = log.output_data if isinstance(log.output_data, dict) else json.loads(log.output_data or '{}')
            
            # Préparer le prompt pour le LLM
            prompt = f"""
            Évalue l'utilité pratique du résultat produit par cet agent:
            
            Agent: {agent.name}
            Opération: {log.operation}
            
            Données d'entrée:
            {json.dumps(input_data, indent=2)}
            
            Résultat produit:
            {json.dumps(output_data, indent=2)}
            
            Attribue un score d'utilité entre 0.0 et 1.0, où:
            - 1.0 signifie que le résultat est extrêmement utile, actionnable et apporte une valeur significative
            - 0.5 signifie que le résultat est moyennement utile ou partiellement actionnable
            - 0.0 signifie que le résultat n'a aucune utilité pratique
            
            Considère la valeur ajoutée, l'actionnabilité et la pertinence pour l'utilisateur.
            Justifie ton évaluation mais retourne uniquement un nombre entre 0.0 et 1.0.
            """
            
            # Obtenir la réponse du LLM
            response = ask_llm(prompt=prompt, max_tokens=50)
            
            # Extraire le score (chercher un nombre entre 0.0 et 1.0)
            text = response.get('text', '')
            import re
            score_match = re.search(r'(\d+\.\d+|\d+)', text)
            
            if score_match:
                score = float(score_match.group(1))
                # S'assurer que le score est dans la plage [0.0, 1.0]
                return max(0.0, min(1.0, score))
            else:
                # Valeur par défaut si aucun score n'est trouvé
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation LLM de l'utilité: {str(e)}")
            return 0.5
    
    def _llm_evaluate_quality(self, log, agent):
        """
        Utilise un LLM pour évaluer la qualité globale d'un résultat.
        
        Args:
            log: Log à évaluer
            agent: Agent concerné
            
        Returns:
            float: Score de qualité estimé (0.0-1.0)
        """
        try:
            # Charger les données d'entrée et de sortie
            input_data = log.input_data if isinstance(log.input_data, dict) else json.loads(log.input_data or '{}')
            output_data = log.output_data if isinstance(log.output_data, dict) else json.loads(log.output_data or '{}')
            
            # Schéma pour la réponse structurée
            evaluation_schema = {
                "evaluation": {
                    "score": 0.75,  # Score global entre 0.0 et 1.0
                    "rationale": "Justification de l'évaluation"
                }
            }
            
            # Préparer le prompt pour le LLM
            prompt = f"""
            Évalue la qualité globale du travail effectué par cet agent:
            
            Agent: {agent.name}
            Opération: {log.operation}
            
            Données d'entrée:
            {json.dumps(input_data, indent=2)}
            
            Résultat produit:
            {json.dumps(output_data, indent=2)}
            
            Évalue la qualité globale en considérant:
            1. La précision et l'exactitude des informations
            2. La complétude et l'exhaustivité du résultat
            3. La pertinence par rapport à la demande initiale
            4. La clarté et la structure du résultat
            5. La valeur ajoutée pour l'utilisateur
            
            Attribue un score global entre 0.0 et 1.0, et justifie brièvement ton évaluation.
            """
            
            # Obtenir la réponse structurée du LLM
            response = generate_structured_response(
                prompt=prompt,
                schema=evaluation_schema,
                system_message="Tu es un expert en évaluation objective de la qualité du travail des agents IA.",
                model="gpt-4.1"
            )
            
            # Extraire le score
            if "evaluation" in response and "score" in response["evaluation"]:
                score = float(response["evaluation"]["score"])
                # S'assurer que le score est dans la plage [0.0, 1.0]
                return max(0.0, min(1.0, score))
            else:
                # Valeur par défaut si aucun score n'est trouvé
                return 0.6
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation LLM de la qualité: {str(e)}")
            return 0.6
    
    def _generate_feedback_text(self, log, agent, criteria_results):
        """
        Génère un feedback textuel basé sur l'évaluation.
        
        Args:
            log: Log évalué
            agent: Agent concerné
            criteria_results: Résultats par critère
            
        Returns:
            str: Feedback textuel
        """
        try:
            # Calculer le score moyen
            avg_score = sum(criteria_results.values()) / len(criteria_results) if criteria_results else 0
            
            # Déterminer les points forts et faibles
            strengths = []
            weaknesses = []
            
            for criterion, score in criteria_results.items():
                if score >= 0.7:
                    strengths.append(criterion)
                elif score <= 0.4:
                    weaknesses.append(criterion)
            
            # Générer le feedback
            feedback = f"Évaluation de l'exécution de {agent.name} ({log.operation}):\n\n"
            
            feedback += f"Score global: {avg_score:.2f}/1.00\n\n"
            
            if strengths:
                feedback += "Points forts:\n"
                for strength in strengths:
                    feedback += f"- {strength.capitalize()}: {criteria_results[strength]:.2f}/1.00\n"
                feedback += "\n"
            
            if weaknesses:
                feedback += "Points à améliorer:\n"
                for weakness in weaknesses:
                    feedback += f"- {weakness.capitalize()}: {criteria_results[weakness]:.2f}/1.00\n"
                feedback += "\n"
            
            # Ajouter des suggestions spécifiques selon le score
            if avg_score < 0.4:
                feedback += "Suggestions d'amélioration:\n"
                if 'accuracy' in weaknesses:
                    feedback += "- Améliorer la précision des données et l'exactitude des résultats\n"
                if 'efficiency' in weaknesses:
                    feedback += "- Optimiser le temps d'exécution et l'utilisation des ressources\n"
                if 'usefulness' in weaknesses:
                    feedback += "- Fournir des résultats plus actionnables et pertinents\n"
                if 'quality' in weaknesses:
                    feedback += "- Améliorer la clarté, la structure et la présentation des résultats\n"
            
            return feedback
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du feedback: {str(e)}")
            return f"Évaluation automatique - Score: {avg_score:.2f}/1.00"
    
    def _save_evaluation(self, log_id, score, criteria_results, feedback_text):
        """
        Enregistre l'évaluation dans la base de données.
        
        Args:
            log_id: ID du log évalué
            score: Score global
            criteria_results: Résultats par critère
            feedback_text: Feedback textuel
        """
        try:
            # Récupérer le log
            log = self.db.query(AgentLog).filter(AgentLog.id == log_id).first()
            
            if not log:
                self.logger.error(f"Log avec ID {log_id} non trouvé")
                return
            
            # Mettre à jour avec le feedback
            log.feedback_score = score
            log.feedback_text = feedback_text
            log.feedback_source = 'agent'
            log.feedback_timestamp = datetime.utcnow()
            
            # Stocker les détails des critères si possible
            try:
                if hasattr(log, 'feedback_details') and criteria_results:
                    log.feedback_details = json.dumps(criteria_results)
            except:
                # Si le champ n'existe pas, ignorer
                pass
            
            self.db.commit()
            
            self.logger.info(f"Évaluation enregistrée pour le log {log_id}: Score {score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de l'évaluation: {str(e)}")
            self.db.rollback()
    
    def _calculate_statistics(self, evaluation_results):
        """
        Calcule des statistiques globales sur les évaluations.
        
        Args:
            evaluation_results: Liste des résultats d'évaluation
            
        Returns:
            dict: Statistiques calculées
        """
        if not evaluation_results:
            return {
                'evaluated_logs': 0,
                'average_score': 0.0,
                'criteria_averages': {}
            }
        
        # Initialiser les statistiques
        stats = {
            'evaluated_logs': len(evaluation_results),
            'average_score': 0.0,
            'criteria_averages': {},
            'agent_stats': {},
            'score_distribution': {
                'excellent': 0,  # >= 0.8
                'good': 0,       # >= 0.6 and < 0.8
                'average': 0,    # >= 0.4 and < 0.6
                'poor': 0        # < 0.4
            }
        }
        
        # Calculer la moyenne globale
        total_score = 0.0
        criteria_totals = {}
        criteria_counts = {}
        
        for eval_result in evaluation_results:
            score = eval_result.get('score', 0.0)
            total_score += score
            
            # Distribution des scores
            if score >= 0.8:
                stats['score_distribution']['excellent'] += 1
            elif score >= 0.6:
                stats['score_distribution']['good'] += 1
            elif score >= 0.4:
                stats['score_distribution']['average'] += 1
            else:
                stats['score_distribution']['poor'] += 1
            
            # Statistiques par critère
            for criterion, criterion_score in eval_result.get('criteria', {}).items():
                if criterion not in criteria_totals:
                    criteria_totals[criterion] = 0.0
                    criteria_counts[criterion] = 0
                
                criteria_totals[criterion] += criterion_score
                criteria_counts[criterion] += 1
            
            # Statistiques par agent
            agent_id = eval_result.get('agent_id')
            agent_name = eval_result.get('agent_name', f'Agent {agent_id}')
            
            if agent_id and agent_id not in stats['agent_stats']:
                stats['agent_stats'][agent_id] = {
                    'name': agent_name,
                    'evaluated_logs': 0,
                    'average_score': 0.0,
                    'scores': []
                }
            
            if agent_id:
                stats['agent_stats'][agent_id]['evaluated_logs'] += 1
                stats['agent_stats'][agent_id]['scores'].append(score)
        
        # Calculer les moyennes
        if stats['evaluated_logs'] > 0:
            stats['average_score'] = total_score / stats['evaluated_logs']
        
        # Moyennes par critère
        for criterion, total in criteria_totals.items():
            count = criteria_counts[criterion]
            if count > 0:
                stats['criteria_averages'][criterion] = total / count
        
        # Moyennes par agent
        for agent_id, agent_stat in stats['agent_stats'].items():
            if agent_stat['scores']:
                agent_stat['average_score'] = sum(agent_stat['scores']) / len(agent_stat['scores'])
                # Supprimer la liste des scores individuels pour alléger
                del agent_stat['scores']
        
        # Convertir la distribution en pourcentages
        total_evals = stats['evaluated_logs']
        for category, count in stats['score_distribution'].items():
            stats['score_distribution'][category] = {
                'count': count,
                'percentage': round((count / total_evals) * 100, 1) if total_evals > 0 else 0.0
            }
        
        return stats
