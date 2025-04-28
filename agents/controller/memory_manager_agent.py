from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
from memory.qdrant import QdrantClient
import json
import time
import datetime
import os

class MemoryManagerAgent(AgentBase):
    def __init__(self):
        super().__init__("MemoryManagerAgent")
        self.prompt_path = "prompts/memory_manager_agent_prompt.txt"
        self.qdrant_client = QdrantClient()
        self.collection_name = "campaign_knowledge"
        self.vector_metadata_file = "logs/vector_metadata.json"
        self.collections_config_file = "logs/collections_config.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensures that necessary files for vector memory management exist"""
        # Vector metadata file to track vector usage and creation dates
        if not os.path.exists(self.vector_metadata_file):
            initial_metadata = {
                "vectors": {},
                "last_maintenance": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.vector_metadata_file, "w") as f:
                json.dump(initial_metadata, f, indent=2)
        
        # Collections configuration file to define thematic collections
        if not os.path.exists(self.collections_config_file):
            initial_config = {
                "thematic_collections": {
                    "prompts": {
                        "description": "Prompts utilisés pour les différents agents",
                        "dimension": 1536,
                        "vector_count": 0,
                        "last_update": datetime.datetime.now().isoformat()
                    },
                    "niches": {
                        "description": "Données relatives aux niches de marché",
                        "dimension": 1536,
                        "vector_count": 0,
                        "last_update": datetime.datetime.now().isoformat()
                    },
                    "strategies": {
                        "description": "Stratégies marketing et commerciales",
                        "dimension": 1536,
                        "vector_count": 0,
                        "last_update": datetime.datetime.now().isoformat()
                    },
                    "campaign_results": {
                        "description": "Résultats et analyses de campagnes",
                        "dimension": 1536,
                        "vector_count": 0,
                        "last_update": datetime.datetime.now().isoformat()
                    }
                },
                "archives": {
                    "enabled": True,
                    "archive_after_days": 90,
                    "purge_after_days": 365,
                    "last_archive_operation": datetime.datetime.now().isoformat()
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(self.collections_config_file, "w") as f:
                json.dump(initial_config, f, indent=2)

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🧠 Gestion de la mémoire vectorielle Qdrant...")

        # Extraire les données de la requête
        operation = input_data.get("operation", "check")
        data = input_data.get("data", {})
        query = input_data.get("query", "")
        collection = input_data.get("collection", self.collection_name)
        
        # Vérifier les opérations de maintenance si nécessaire
        if operation in ["check", "maintenance"]:
            maintenance_needed = self._check_maintenance_needed()
            if maintenance_needed and operation == "check":
                print(f"[{self.name}] ⚠️ Maintenance recommandée pour les collections vectorielles")
                
        # Charger le prompt depuis le fichier
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
        except Exception as e:
            result = {"error": f"Erreur lors du chargement du prompt: {str(e)}", "operation": operation, "status": "FAILED"}
            log_agent(self.name, input_data, result)
            return result

        # Préparer le contexte pour le LLM
        memory_stats = self._get_memory_stats(collection)
        collections_config = self._load_collections_config()
        vector_metadata = self._load_vector_metadata()
        
        # Construire le prompt avec les données contextuelles
        prompt = prompt_template
        prompt = prompt.replace("{{operation}}", operation)
        prompt = prompt.replace("{{collection_status}}", json.dumps(memory_stats))
        prompt = prompt.replace("{{thematic_collections}}", json.dumps(collections_config.get("thematic_collections", {})))
        prompt = prompt.replace("{{archives_config}}", json.dumps(collections_config.get("archives", {})))
        
        if operation == "query":
            prompt = prompt.replace("{{query}}", query)
            prompt = prompt.replace("{{collection}}", collection)
        elif operation in ["store", "clean", "update"]:
            prompt = prompt.replace("{{data}}", json.dumps(data))
            prompt = prompt.replace("{{collection}}", collection)
        elif operation == "detect_obsolete":
            vector_age_data = self._analyze_vector_age(vector_metadata)
            prompt = prompt.replace("{{vector_age_data}}", json.dumps(vector_age_data))
        elif operation == "organize_collections":
            prompt = prompt.replace("{{current_organization}}", json.dumps(self._get_current_organization()))
        elif operation == "archive_plan":
            archive_candidates = self._identify_archive_candidates(vector_metadata, collections_config)
            prompt = prompt.replace("{{archive_candidates}}", json.dumps(archive_candidates))
        
        # Appeler GPT-4.1 pour la décision
        response = ask_gpt_4_1(prompt)
        
        # Exécuter l'opération demandée
        result = self._execute_memory_operation(operation, response, data, query, collection, vector_metadata, collections_config)
        
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _get_memory_stats(self, collection_name):
        """
        Récupère les statistiques sur la mémoire vectorielle
        """
        try:
            # Dans une implémentation réelle, cette fonction interrogerait Qdrant
            # pour obtenir des statistiques sur la collection
            collection_info = self.qdrant_client.get_collection(collection_name)
            
            if not collection_info:
                return {
                    "collection_name": collection_name,
                    "exists": False,
                    "health_status": "NOT_FOUND"
                }
            
            # Analyse des vecteurs pour estimer les doublons
            duplicates_estimate = self._estimate_duplicates(collection_name)
            
            # Récupérer la dernière mise à jour depuis les métadonnées
            vector_metadata = self._load_vector_metadata()
            last_update = vector_metadata.get("last_updated", datetime.datetime.now().isoformat())
            
            return {
                "collection_name": collection_name,
                "exists": True,
                "vectors_count": collection_info.get("vectors_count", 0),
                "dimensions": 1536,  # Simulé, dans la réalité on récupérerait cette info
                "duplicates_estimate": duplicates_estimate,
                "last_update": last_update,
                "health_status": collection_info.get("status", "UNKNOWN")
            }
        except Exception as e:
            return {
                "collection_name": collection_name,
                "error": str(e),
                "health_status": "ERROR"
            }
    
    def _estimate_duplicates(self, collection_name):
        """
        Estime le nombre de vecteurs en doublon dans une collection
        """
        try:
            # Dans une implémentation réelle, on utiliserait une requête à Qdrant
            duplicates = self.qdrant_client.get_duplicates(collection_name)
            return len(duplicates)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'estimation des doublons: {str(e)}")
            return 0
    
    def _check_maintenance_needed(self):
        """
        Vérifie si une maintenance des collections est nécessaire
        """
        try:
            # Charger les métadonnées
            vector_metadata = self._load_vector_metadata()
            collections_config = self._load_collections_config()
            
            # Vérifier la date de dernière maintenance
            last_maintenance = datetime.datetime.fromisoformat(vector_metadata.get("last_maintenance", "2000-01-01T00:00:00"))
            now = datetime.datetime.now()
            
            # Si la dernière maintenance a plus de 7 jours, recommander une maintenance
            if (now - last_maintenance).days > 7:
                return True
            
            # Vérifier si des vecteurs à archiver existent
            archive_candidates = self._identify_archive_candidates(vector_metadata, collections_config)
            if archive_candidates.get("to_archive", []) or archive_candidates.get("to_purge", []):
                return True
            
            # Vérifier si le taux de doublons est élevé
            for collection_name in [self.collection_name] + list(collections_config.get("thematic_collections", {}).keys()):
                stats = self._get_memory_stats(collection_name)
                if stats.get("exists", False):
                    vectors_count = stats.get("vectors_count", 0)
                    duplicates = stats.get("duplicates_estimate", 0)
                    
                    if vectors_count > 0 and duplicates / vectors_count > 0.05:  # Plus de 5% de doublons
                        return True
            
            return False
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la vérification de maintenance: {str(e)}")
            return False
    
    def _analyze_vector_age(self, vector_metadata):
        """
        Analyse l'âge des vecteurs pour détecter les obsolètes
        """
        vectors = vector_metadata.get("vectors", {})
        now = datetime.datetime.now()
        
        age_categories = {
            "recent": [],      # Moins de 30 jours
            "medium": [],      # 30 à 90 jours
            "old": [],         # 90 à 180 jours
            "very_old": []     # Plus de 180 jours
        }
        
        for vector_id, info in vectors.items():
            if "created_at" in info:
                try:
                    created_at = datetime.datetime.fromisoformat(info["created_at"])
                    days_old = (now - created_at).days
                    
                    if days_old <= 30:
                        age_categories["recent"].append(vector_id)
                    elif days_old <= 90:
                        age_categories["medium"].append(vector_id)
                    elif days_old <= 180:
                        age_categories["old"].append(vector_id)
                    else:
                        age_categories["very_old"].append(vector_id)
                except Exception:
                    # En cas d'erreur de date, considérer le vecteur comme ancien
                    age_categories["very_old"].append(vector_id)
        
        # Ajouter les statistiques d'usage pour détecter les vecteurs non utilisés
        usage_categories = {
            "unused": [],      # Jamais utilisé
            "rarely_used": [], # Utilisé moins de 5 fois
            "used": [],        # Utilisé 5 à 20 fois
            "heavily_used": [] # Utilisé plus de 20 fois
        }
        
        for vector_id, info in vectors.items():
            usage_count = info.get("usage_count", 0)
            
            if usage_count == 0:
                usage_categories["unused"].append(vector_id)
            elif usage_count < 5:
                usage_categories["rarely_used"].append(vector_id)
            elif usage_count <= 20:
                usage_categories["used"].append(vector_id)
            else:
                usage_categories["heavily_used"].append(vector_id)
        
        # Identifier les vecteurs de campagnes échouées
        failed_campaigns = []
        for vector_id, info in vectors.items():
            if info.get("campaign_success") is False:
                failed_campaigns.append(vector_id)
        
        return {
            "age_categories": age_categories,
            "usage_categories": usage_categories,
            "failed_campaigns": failed_campaigns,
            "total_vectors": len(vectors)
        }
    
    def _get_current_organization(self):
        """
        Analyse l'organisation actuelle des collections
        """
        collections = self._load_collections_config().get("thematic_collections", {})
        
        # Dans une implémentation réelle, on interrogerait Qdrant pour chaque collection
        current_organization = {}
        
        for collection_name, info in collections.items():
            collection_info = self.qdrant_client.get_collection(collection_name)
            
            if collection_info:
                current_organization[collection_name] = {
                    "exists": True,
                    "vectors_count": collection_info.get("vectors_count", 0),
                    "description": info.get("description", ""),
                    "last_update": info.get("last_update", "")
                }
            else:
                current_organization[collection_name] = {
                    "exists": False,
                    "vectors_count": 0,
                    "description": info.get("description", ""),
                    "last_update": info.get("last_update", "")
                }
        
        # Ajouter la collection principale
        main_collection = self.qdrant_client.get_collection(self.collection_name)
        if main_collection:
            current_organization["main"] = {
                "collection_name": self.collection_name,
                "exists": True,
                "vectors_count": main_collection.get("vectors_count", 0),
                "description": "Collection principale",
                "last_update": ""
            }
        
        return current_organization
    
    def _identify_archive_candidates(self, vector_metadata, collections_config):
        """
        Identifie les vecteurs candidats à l'archivage ou à la purge
        """
        vectors = vector_metadata.get("vectors", {})
        now = datetime.datetime.now()
        
        # Récupérer les seuils d'archivage et de purge
        archives_config = collections_config.get("archives", {})
        archive_after_days = archives_config.get("archive_after_days", 90)
        purge_after_days = archives_config.get("purge_after_days", 365)
        
        to_archive = []
        to_purge = []
        
        for vector_id, info in vectors.items():
            if "created_at" in info:
                try:
                    created_at = datetime.datetime.fromisoformat(info["created_at"])
                    days_old = (now - created_at).days
                    
                    # Candidats à la purge (très vieux ou jamais utilisés)
                    if days_old > purge_after_days or (days_old > archive_after_days and info.get("usage_count", 0) == 0):
                        to_purge.append({
                            "vector_id": vector_id,
                            "days_old": days_old,
                            "usage_count": info.get("usage_count", 0),
                            "last_used": info.get("last_used", "never"),
                            "reason": "age_and_unused" if info.get("usage_count", 0) == 0 else "very_old"
                        })
                    # Candidats à l'archivage (vieux ou peu utilisés)
                    elif days_old > archive_after_days:
                        to_archive.append({
                            "vector_id": vector_id,
                            "days_old": days_old,
                            "usage_count": info.get("usage_count", 0),
                            "last_used": info.get("last_used", "never"),
                            "reason": "old"
                        })
                except Exception:
                    # En cas d'erreur de date, considérer comme candidat à l'archivage
                    to_archive.append({
                        "vector_id": vector_id,
                        "days_old": -1,
                        "usage_count": info.get("usage_count", 0),
                        "last_used": info.get("last_used", "never"),
                        "reason": "date_error"
                    })
        
        # Ajouter les vecteurs de campagnes échouées à l'archivage
        for vector_id, info in vectors.items():
            if info.get("campaign_success") is False and vector_id not in [a["vector_id"] for a in to_archive] and vector_id not in [p["vector_id"] for p in to_purge]:
                to_archive.append({
                    "vector_id": vector_id,
                    "days_old": -1,
                    "usage_count": info.get("usage_count", 0),
                    "last_used": info.get("last_used", "never"),
                    "reason": "failed_campaign"
                })
        
        return {
            "to_archive": to_archive,
            "to_purge": to_purge,
            "archive_after_days": archive_after_days,
            "purge_after_days": purge_after_days
        }
    
    def _execute_memory_operation(self, operation, decision, data, query, collection, vector_metadata, collections_config):
        """
        Exécute l'opération de mémoire selon la décision du LLM
        """
        result = {
            "operation": operation,
            "collection": collection,
            "status": "COMPLETED",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            if operation == "store":
                # Stocker de nouvelles connaissances dans Qdrant
                if "vectors_to_store" in decision:
                    # Mise à jour des métadonnées de vecteurs
                    vectors_to_store = decision.get("vectors_to_store", [])
                    stored_vector_ids = self._store_vectors(vectors_to_store, collection)
                    
                    # Enregistrer les métadonnées pour les nouveaux vecteurs
                    now = datetime.datetime.now().isoformat()
                    for vector_id in stored_vector_ids:
                        vector_metadata["vectors"][vector_id] = {
                            "created_at": now,
                            "collection": collection,
                            "usage_count": 0,
                            "last_used": None,
                            "content_type": decision.get("content_type", "unknown"),
                            "tags": decision.get("tags", [])
                        }
                    
                    # Mise à jour du fichier de métadonnées
                    vector_metadata["last_updated"] = now
                    self._save_vector_metadata(vector_metadata)
                    
                    result["stored_count"] = len(stored_vector_ids)
                    result["stored_ids"] = stored_vector_ids
                    result["details"] = "Vecteurs stockés avec succès"
            
            elif operation == "clean":
                # Nettoyer les doublons ou données obsolètes
                if "vectors_to_clean" in decision:
                    # Simulation de nettoyage
                    vectors_to_clean = decision.get("vectors_to_clean", [])
                    cleaned_count = self._clean_vectors(vectors_to_clean, collection)
                    
                    # Mise à jour des métadonnées
                    for vector_id in vectors_to_clean:
                        if vector_id in vector_metadata["vectors"]:
                            del vector_metadata["vectors"][vector_id]
                    
                    # Mise à jour du fichier de métadonnées
                    vector_metadata["last_updated"] = datetime.datetime.now().isoformat()
                    self._save_vector_metadata(vector_metadata)
                    
                    result["cleaned_count"] = cleaned_count
                    result["details"] = "Nettoyage de vecteurs effectué"
            
            elif operation == "query":
                # Recherche d'informations dans la mémoire
                if "search_results" in decision:
                    result["results"] = decision.get("search_results", [])
                    result["details"] = f"Requête exécutée, {len(result['results'])} résultats trouvés"
                    
                    # Mise à jour des statistiques d'utilisation
                    for search_result in decision.get("search_results", []):
                        vector_id = search_result.get("id")
                        if vector_id and vector_id in vector_metadata["vectors"]:
                            vector_metadata["vectors"][vector_id]["usage_count"] = vector_metadata["vectors"][vector_id].get("usage_count", 0) + 1
                            vector_metadata["vectors"][vector_id]["last_used"] = datetime.datetime.now().isoformat()
                    
                    # Mise à jour du fichier de métadonnées
                    vector_metadata["last_updated"] = datetime.datetime.now().isoformat()
                    self._save_vector_metadata(vector_metadata)
            
            elif operation == "update":
                # Mise à jour de vecteurs existants
                if "vectors_to_update" in decision:
                    # Simulation de mise à jour
                    vectors_to_update = decision.get("vectors_to_update", [])
                    updated_count = self._update_vectors(vectors_to_update, collection)
                    
                    # Mise à jour des métadonnées
                    for vector_update in vectors_to_update:
                        vector_id = vector_update.get("id")
                        if vector_id and vector_id in vector_metadata["vectors"]:
                            # Mettre à jour les tags si spécifiés
                            if "tags" in vector_update:
                                vector_metadata["vectors"][vector_id]["tags"] = vector_update["tags"]
                            
                            # Mettre à jour d'autres métadonnées si nécessaire
                            if "content_type" in vector_update:
                                vector_metadata["vectors"][vector_id]["content_type"] = vector_update["content_type"]
                    
                    # Mise à jour du fichier de métadonnées
                    vector_metadata["last_updated"] = datetime.datetime.now().isoformat()
                    self._save_vector_metadata(vector_metadata)
                    
                    result["updated_count"] = updated_count
                    result["details"] = "Mise à jour de vecteurs effectuée"
            
            elif operation == "check":
                # Vérification de l'état de la mémoire
                result["memory_status"] = decision.get("memory_status", {})
                result["details"] = decision.get("details", "Vérification de mémoire effectuée")
            
            elif operation == "detect_obsolete":
                # Détection de vecteurs obsolètes
                result["obsolete_vectors"] = decision.get("obsolete_vectors", [])
                result["obsolete_count"] = len(decision.get("obsolete_vectors", []))
                result["details"] = decision.get("details", "Analyse d'obsolescence effectuée")
            
            elif operation == "organize_collections":
                # Organisation des collections thématiques
                if "collection_organization" in decision:
                    organization_plan = decision.get("collection_organization", {})
                    organization_results = self._organize_collections(organization_plan, collections_config)
                    
                    # Mise à jour de la configuration des collections
                    collections_config["last_updated"] = datetime.datetime.now().isoformat()
                    self._save_collections_config(collections_config)
                    
                    result["organization_results"] = organization_results
                    result["details"] = "Organisation des collections effectuée"
            
            elif operation == "archive_plan":
                # Plan d'archivage et de purge
                if "archive_plan" in decision:
                    archive_plan = decision.get("archive_plan", {})
                    archive_results = self._execute_archive_plan(archive_plan, vector_metadata, collections_config)
                    
                    # Mise à jour des métadonnées et de la configuration
                    now = datetime.datetime.now().isoformat()
                    vector_metadata["last_maintenance"] = now
                    vector_metadata["last_updated"] = now
                    collections_config["archives"]["last_archive_operation"] = now
                    collections_config["last_updated"] = now
                    
                    self._save_vector_metadata(vector_metadata)
                    self._save_collections_config(collections_config)
                    
                    result["archive_results"] = archive_results
                    result["details"] = "Plan d'archivage exécuté"
            
            elif operation == "maintenance":
                # Maintenance complète de la mémoire vectorielle
                maintenance_results = self._perform_maintenance(decision, vector_metadata, collections_config)
                
                # Mise à jour des métadonnées
                now = datetime.datetime.now().isoformat()
                vector_metadata["last_maintenance"] = now
                vector_metadata["last_updated"] = now
                
                self._save_vector_metadata(vector_metadata)
                
                result["maintenance_results"] = maintenance_results
                result["details"] = "Maintenance complète effectuée"
                
            else:
                result["status"] = "FAILED"
                result["error"] = f"Opération non reconnue: {operation}"
        
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        return result
    
    def _store_vectors(self, vectors_to_store, collection_name):
        """
        Stocke des vecteurs dans la collection spécifiée.
        Retourne la liste des IDs des vecteurs stockés.
        """
        # Dans une implémentation réelle, on appellerait l'API de Qdrant
        # Ici, on simule le stockage et on génère des IDs factices
        
        stored_ids = []
        for i in range(len(vectors_to_store)):
            vector_id = f"vector_{int(time.time())}_{i}"
            stored_ids.append(vector_id)
        
        # Mise à jour du compteur de vecteurs dans la configuration des collections
        collections_config = self._load_collections_config()
        if collection_name in collections_config.get("thematic_collections", {}):
            collections_config["thematic_collections"][collection_name]["vector_count"] += len(vectors_to_store)
            collections_config["thematic_collections"][collection_name]["last_update"] = datetime.datetime.now().isoformat()
            self._save_collections_config(collections_config)
        
        print(f"[{self.name}] ✅ {len(stored_ids)} vecteurs stockés dans la collection {collection_name}")
        return stored_ids
    
    def _clean_vectors(self, vectors_to_clean, collection_name):
        """
        Nettoie (supprime) des vecteurs dans la collection spécifiée.
        Retourne le nombre de vecteurs nettoyés.
        """
        # Dans une implémentation réelle, on appellerait l'API de Qdrant
        cleaned_count = len(vectors_to_clean)
        
        # Mise à jour du compteur de vecteurs dans la configuration des collections
        collections_config = self._load_collections_config()
        if collection_name in collections_config.get("thematic_collections", {}):
            collections_config["thematic_collections"][collection_name]["vector_count"] = max(0, collections_config["thematic_collections"][collection_name]["vector_count"] - cleaned_count)
            collections_config["thematic_collections"][collection_name]["last_update"] = datetime.datetime.now().isoformat()
            self._save_collections_config(collections_config)
        
        print(f"[{self.name}] 🧹 {cleaned_count} vecteurs nettoyés dans la collection {collection_name}")
        return cleaned_count
    
    def _update_vectors(self, vectors_to_update, collection_name):
        """
        Met à jour des vecteurs dans la collection spécifiée.
        Retourne le nombre de vecteurs mis à jour.
        """
        # Dans une implémentation réelle, on appellerait l'API de Qdrant
        updated_count = len(vectors_to_update)
        
        # Mise à jour de la date de dernière mise à jour dans la configuration des collections
        collections_config = self._load_collections_config()
        if collection_name in collections_config.get("thematic_collections", {}):
            collections_config["thematic_collections"][collection_name]["last_update"] = datetime.datetime.now().isoformat()
            self._save_collections_config(collections_config)
        
        print(f"[{self.name}] 🔄 {updated_count} vecteurs mis à jour dans la collection {collection_name}")
        return updated_count
    
    def _organize_collections(self, organization_plan, collections_config):
        """
        Organise les collections thématiques selon le plan fourni.
        Retourne les résultats de l'organisation.
        """
        results = {
            "created_collections": [],
            "updated_collections": [],
            "moved_vectors": 0
        }
        
        # Créer ou mettre à jour les collections
        for collection_name, config in organization_plan.get("collections", {}).items():
            if collection_name not in collections_config.get("thematic_collections", {}):
                # Créer la nouvelle collection
                self.qdrant_client.create_collection(collection_name, config.get("dimension", 1536))
                
                # Ajouter à la configuration
                collections_config["thematic_collections"][collection_name] = {
                    "description": config.get("description", ""),
                    "dimension": config.get("dimension", 1536),
                    "vector_count": 0,
                    "last_update": datetime.datetime.now().isoformat()
                }
                
                results["created_collections"].append(collection_name)
            else:
                # Mettre à jour la configuration existante
                collections_config["thematic_collections"][collection_name]["description"] = config.get("description", collections_config["thematic_collections"][collection_name]["description"])
                
                results["updated_collections"].append(collection_name)
        
        # Déplacer les vecteurs selon le plan
        for move_operation in organization_plan.get("moves", []):
            source_collection = move_operation.get("from")
            target_collection = move_operation.get("to")
            vector_ids = move_operation.get("vector_ids", [])
            
            if source_collection and target_collection and vector_ids:
                # Dans une implémentation réelle, on déplacerait les vecteurs dans Qdrant
                moved_count = len(vector_ids)
                
                # Mettre à jour les compteurs dans la configuration
                if source_collection in collections_config.get("thematic_collections", {}) and target_collection in collections_config.get("thematic_collections", {}):
                    collections_config["thematic_collections"][source_collection]["vector_count"] = max(0, collections_config["thematic_collections"][source_collection]["vector_count"] - moved_count)
                    collections_config["thematic_collections"][target_collection]["vector_count"] += moved_count
                
                # Mettre à jour les métadonnées des vecteurs
                vector_metadata = self._load_vector_metadata()
                for vector_id in vector_ids:
                    if vector_id in vector_metadata.get("vectors", {}):
                        vector_metadata["vectors"][vector_id]["collection"] = target_collection
                
                self._save_vector_metadata(vector_metadata)
                
                results["moved_vectors"] += moved_count
        
        return results
    
    def _execute_archive_plan(self, archive_plan, vector_metadata, collections_config):
        """
        Exécute un plan d'archivage de vecteurs obsolètes.
        Retourne les résultats de l'opération.
        """
        results = {
            "archived_count": 0,
            "purged_count": 0
        }
        
        # Créer la collection d'archives si elle n'existe pas
        archive_collection = archive_plan.get("archive_collection", "archives")
        if archive_collection not in collections_config.get("thematic_collections", {}):
            self.qdrant_client.create_collection(archive_collection, 1536)
            collections_config["thematic_collections"][archive_collection] = {
                "description": "Archives de vecteurs obsolètes",
                "dimension": 1536,
                "vector_count": 0,
                "last_update": datetime.datetime.now().isoformat()
            }
        
        # Archiver les vecteurs
        vectors_to_archive = archive_plan.get("vectors_to_archive", [])
        for vector_id in vectors_to_archive:
            if vector_id in vector_metadata.get("vectors", {}):
                # Récupérer la collection d'origine
                source_collection = vector_metadata["vectors"][vector_id].get("collection", self.collection_name)
                
                # Dans une implémentation réelle, on déplacerait le vecteur vers la collection d'archives
                
                # Mettre à jour les métadonnées
                vector_metadata["vectors"][vector_id]["collection"] = archive_collection
                vector_metadata["vectors"][vector_id]["archived_at"] = datetime.datetime.now().isoformat()
                vector_metadata["vectors"][vector_id]["archived_reason"] = "obsolescence"
                
                # Mettre à jour les compteurs
                if source_collection in collections_config.get("thematic_collections", {}):
                    collections_config["thematic_collections"][source_collection]["vector_count"] = max(0, collections_config["thematic_collections"][source_collection].get("vector_count", 0) - 1)
                
                collections_config["thematic_collections"][archive_collection]["vector_count"] = collections_config["thematic_collections"][archive_collection].get("vector_count", 0) + 1
                
                results["archived_count"] += 1
        
        # Purger les vecteurs (suppression complète)
        vectors_to_purge = archive_plan.get("vectors_to_purge", [])
        for vector_id in vectors_to_purge:
            if vector_id in vector_metadata.get("vectors", {}):
                # Récupérer la collection d'origine
                source_collection = vector_metadata["vectors"][vector_id].get("collection", self.collection_name)
                
                # Dans une implémentation réelle, on supprimerait le vecteur de Qdrant
                
                # Supprimer des métadonnées
                del vector_metadata["vectors"][vector_id]
                
                # Mettre à jour les compteurs
                if source_collection in collections_config.get("thematic_collections", {}):
                    collections_config["thematic_collections"][source_collection]["vector_count"] = max(0, collections_config["thematic_collections"][source_collection].get("vector_count", 0) - 1)
                
                results["purged_count"] += 1
        
        return results
    
    def _perform_maintenance(self, decision, vector_metadata, collections_config):
        """
        Exécute une maintenance complète des collections vectorielles.
        """
        results = {
            "cleaned_duplicates": 0,
            "archived_vectors": 0,
            "purged_vectors": 0,
            "reorganized_collections": False,
            "details": []
        }
        
        # 1. Nettoyage des doublons
        if "duplicates_to_clean" in decision:
            duplicates = decision.get("duplicates_to_clean", [])
            for duplicate_set in duplicates:
                # Garder le premier vecteur, supprimer les autres
                if len(duplicate_set) > 1:
                    vectors_to_remove = duplicate_set[1:]
                    
                    # Nettoyer les vecteurs en doublon
                    for vector_id in vectors_to_remove:
                        if vector_id in vector_metadata.get("vectors", {}):
                            # Récupérer la collection
                            collection = vector_metadata["vectors"][vector_id].get("collection", self.collection_name)
                            
                            # Dans une implémentation réelle, on supprimerait le vecteur de Qdrant
                            
                            # Supprimer des métadonnées
                            del vector_metadata["vectors"][vector_id]
                            
                            # Mettre à jour les compteurs
                            if collection in collections_config.get("thematic_collections", {}):
                                collections_config["thematic_collections"][collection]["vector_count"] = max(0, collections_config["thematic_collections"][collection].get("vector_count", 0) - 1)
                            
                            results["cleaned_duplicates"] += 1
        
        # 2. Archivage des vecteurs obsolètes
        if "vectors_to_archive" in decision:
            archive_plan = {
                "archive_collection": "archives",
                "vectors_to_archive": decision.get("vectors_to_archive", []),
                "vectors_to_purge": decision.get("vectors_to_purge", [])
            }
            
            archive_results = self._execute_archive_plan(archive_plan, vector_metadata, collections_config)
            
            results["archived_vectors"] = archive_results.get("archived_count", 0)
            results["purged_vectors"] = archive_results.get("purged_count", 0)
        
        # 3. Réorganisation des collections si recommandé
        if decision.get("reorganize_collections", False) and "collection_organization" in decision:
            organization_plan = decision.get("collection_organization", {})
            organization_results = self._organize_collections(organization_plan, collections_config)
            
            results["reorganized_collections"] = True
            results["created_collections"] = organization_results.get("created_collections", [])
            results["updated_collections"] = organization_results.get("updated_collections", [])
            results["moved_vectors"] = organization_results.get("moved_vectors", 0)
        
        # 4. Ajouter des détails et recommandations
        if "maintenance_details" in decision:
            results["details"] = decision.get("maintenance_details", [])
        
        return results
    
    def _load_vector_metadata(self):
        """
        Charge les métadonnées des vecteurs depuis le fichier.
        """
        try:
            with open(self.vector_metadata_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des métadonnées: {str(e)}")
            return {"vectors": {}, "last_updated": datetime.datetime.now().isoformat()}
    
    def _save_vector_metadata(self, metadata):
        """
        Sauvegarde les métadonnées des vecteurs dans le fichier.
        """
        try:
            with open(self.vector_metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde des métadonnées: {str(e)}")
            return False
    
    def _load_collections_config(self):
        """
        Charge la configuration des collections depuis le fichier.
        """
        try:
            with open(self.collections_config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement de la configuration: {str(e)}")
            return {
                "thematic_collections": {},
                "archives": {
                    "enabled": True,
                    "archive_after_days": 90,
                    "purge_after_days": 365
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
    
    def _save_collections_config(self, config):
        """
        Sauvegarde la configuration des collections dans le fichier.
        """
        try:
            with open(self.collections_config_file, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde de la configuration: {str(e)}")
            return False
