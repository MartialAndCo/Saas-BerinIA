"""
Module d'interface avec le stockage vectoriel Qdrant.
Fournit des méthodes pour stocker et récupérer des embeddings vectoriels.
"""

import os
from typing import List, Dict, Any, Optional, Union
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from utils.embeddings import get_model_embedding, batch_get_embeddings
from utils.config import get_config

# Configuration du logging
logger = logging.getLogger(__name__)
config = get_config()

class VectorStore:
    """
    Classe d'intégration avec Qdrant pour le stockage et la récupération
    d'embeddings vectoriels.
    """
    
    def __init__(
        self, 
        collection_name: str,
        host: str = None,
        port: int = None,
        embedding_size: int = 1536,  # Taille par défaut pour Ada-002
        embedding_model: str = "text-embedding-ada-002"
    ):
        """
        Initialise la connexion avec Qdrant.
        
        Args:
            collection_name (str): Nom de la collection à utiliser/créer
            host (str): Hôte du serveur Qdrant (None pour utiliser la config)
            port (int): Port du serveur Qdrant (None pour utiliser la config)
            embedding_size (int): Taille des vecteurs d'embedding
            embedding_model (str): Modèle à utiliser pour les embeddings
        """
        self.collection_name = collection_name
        
        # Utiliser les valeurs de configuration si non spécifiées
        if host is None:
            host = config.qdrant_host
        if port is None:
            port = config.qdrant_port
        
        self.client = QdrantClient(host=host, port=port)
        self.embedding_size = embedding_size
        self.embedding_model = embedding_model
        
        # Initialise ou vérifie la collection
        self._initialize_collection()
        
    def _initialize_collection(self) -> None:
        """
        Initialise la collection si elle n'existe pas déjà.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.embedding_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' créée avec succès")
            else:
                logger.info(f"Collection '{self.collection_name}' existe déjà")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection: {str(e)}")
            raise
    
    def add_text(
        self, 
        text: str, 
        metadata: Dict[str, Any], 
        text_id: Optional[str] = None
    ) -> str:
        """
        Ajoute un texte à la collection.
        
        Args:
            text (str): Le texte à vectoriser et stocker
            metadata (Dict[str, Any]): Métadonnées associées au texte
            text_id (Optional[str]): ID optionnel pour le point
            
        Returns:
            str: L'ID du point ajouté
        """
        # Obtenir l'embedding du texte
        embedding = get_model_embedding(text, model=self.embedding_model)
        
        if not embedding:
            logger.error("Échec de la génération de l'embedding")
            return None
        
        # Générer un ID si non fourni
        if not text_id:
            import uuid
            text_id = str(uuid.uuid4())
        
        # Ajouter les métadonnées et le texte original
        payload = {
            **metadata,
            "text": text
        }
        
        # Upsert le point dans Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=text_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"Point ajouté avec ID: {text_id}")
            return text_id
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du point: {str(e)}")
            return None
    
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Ajoute plusieurs textes à la collection.
        
        Args:
            texts (List[str]): Les textes à vectoriser et stocker
            metadatas (List[Dict[str, Any]]): Métadonnées associées aux textes
            ids (Optional[List[str]]): IDs optionnels pour les points
            
        Returns:
            List[str]: Les IDs des points ajoutés
        """
        if len(texts) != len(metadatas):
            raise ValueError("Le nombre de textes et de métadonnées doit être identique")
        
        if ids and len(ids) != len(texts):
            raise ValueError("Le nombre d'IDs doit correspondre au nombre de textes")
        
        # Générer des IDs si non fournis
        if not ids:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Obtenir les embeddings en batch
        embeddings = batch_get_embeddings(texts, model=self.embedding_model)
        
        # Préparer les points
        points = []
        valid_ids = []
        
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            if not embedding:
                logger.warning(f"Échec de la génération de l'embedding pour le texte {i}, ignoré")
                continue
                
            payload = {
                **metadatas[i],
                "text": text
            }
            
            points.append(
                models.PointStruct(
                    id=ids[i],
                    vector=embedding,
                    payload=payload
                )
            )
            valid_ids.append(ids[i])
        
        # Upsert les points dans Qdrant
        if points:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                logger.info(f"{len(points)} points ajoutés sur {len(texts)} textes")
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout des points: {str(e)}")
                return []
        
        return valid_ids
    
    def search_similar(
        self, 
        query: str, 
        limit: int = 5, 
        filter_condition: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche les textes similaires à une requête.
        
        Args:
            query (str): La requête de recherche
            limit (int): Nombre maximum de résultats
            filter_condition (Optional[Dict[str, Any]]): Condition de filtrage
            
        Returns:
            List[Dict[str, Any]]: Les résultats de recherche avec scores et métadonnées
        """
        # Obtenir l'embedding de la requête
        query_embedding = get_model_embedding(query, model=self.embedding_model)
        
        if not query_embedding:
            logger.error("Échec de la génération de l'embedding pour la requête")
            return []
        
        # Convertir la condition de filtrage en modèle Qdrant si fournie
        filter_model = None
        if filter_condition:
            filter_model = models.Filter(**filter_condition)
        
        # Effectuer la recherche
        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=filter_model
            )
            
            # Formater les résultats
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            return []
    
    def delete_by_ids(self, ids: List[str]) -> bool:
        """
        Supprime des points par leur ID.
        
        Args:
            ids (List[str]): Liste des IDs à supprimer
            
        Returns:
            bool: True si réussi, False sinon
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            logger.info(f"{len(ids)} points supprimés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des points: {str(e)}")
            return False
    
    def delete_by_filter(self, filter_condition: Dict[str, Any]) -> bool:
        """
        Supprime des points selon une condition de filtrage.
        
        Args:
            filter_condition (Dict[str, Any]): Condition de filtrage
            
        Returns:
            bool: True si réussi, False sinon
        """
        try:
            filter_model = models.Filter(**filter_condition)
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_model
            )
            logger.info("Points supprimés selon le filtre spécifié")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression par filtre: {str(e)}")
            return False
    
    def update_metadata(self, point_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Met à jour les métadonnées d'un point.
        
        Args:
            point_id (str): ID du point à mettre à jour
            metadata (Dict[str, Any]): Nouvelles métadonnées
            
        Returns:
            bool: True si réussi, False sinon
        """
        try:
            # Récupérer le point actuel
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )
            
            if not points:
                logger.error(f"Point avec ID {point_id} non trouvé")
                return False
            
            # Conserver le texte original
            text = points[0].payload.get("text", "")
            
            # Mettre à jour le payload
            payload = {
                **metadata,
                "text": text
            }
            
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=payload,
                points=[point_id]
            )
            logger.info(f"Métadonnées mises à jour pour le point {point_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métadonnées: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur la collection.
        
        Returns:
            Dict[str, Any]: Informations sur la collection
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": getattr(collection_info, 'vectors_count', 0),
                "points_count": getattr(collection_info, 'points_count', 0),
                "status": getattr(collection_info, 'status', 'unknown')
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations de collection: {str(e)}")
            return {}
