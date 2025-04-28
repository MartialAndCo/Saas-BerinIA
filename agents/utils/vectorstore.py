import os
from typing import List, Dict, Any, Optional, Union
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from .llm import get_model_embedding

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Classe d'intégration avec Qdrant pour le stockage et la récupération
    d'embeddings vectoriels.
    """
    
    def __init__(
        self, 
        collection_name: str,
        host: str = "localhost",
        port: int = 6333,
        embedding_size: int = 1536,  # Taille par défaut pour Ada-002
        embedding_model: str = "text-embedding-ada-002"
    ):
        """
        Initialise la connexion avec Qdrant.
        
        Args:
            collection_name (str): Nom de la collection à utiliser/créer
            host (str): Hôte du serveur Qdrant
            port (int): Port du serveur Qdrant
            embedding_size (int): Taille des vecteurs d'embedding
            embedding_model (str): Modèle à utiliser pour les embeddings
        """
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        self.embedding_size = embedding_size
        self.embedding_model = embedding_model
        
        # Initialise ou vérifie la collection
        self._initialize_collection()
        
    def _initialize_collection(self) -> None:
        """
        Initialise la collection si elle n'existe pas déjà.
        """
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
        
        # Préparer les points
        points = []
        for i, text in enumerate(texts):
            embedding = get_model_embedding(text, model=self.embedding_model)
            
            if not embedding:
                logger.error(f"Échec de la génération de l'embedding pour le texte {i}")
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
        
        # Upsert les points dans Qdrant
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"{len(points)} points ajoutés")
        
        return ids
    
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
    
    def delete_by_ids(self, ids: List[str]) -> None:
        """
        Supprime des points par leur ID.
        
        Args:
            ids (List[str]): Liste des IDs à supprimer
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=ids
            )
        )
        logger.info(f"{len(ids)} points supprimés")
    
    def delete_by_filter(self, filter_condition: Dict[str, Any]) -> None:
        """
        Supprime des points selon une condition de filtrage.
        
        Args:
            filter_condition (Dict[str, Any]): Condition de filtrage
        """
        filter_model = models.Filter(**filter_condition)
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=filter_model
        )
        logger.info("Points supprimés selon le filtre spécifié")
    
    def update_metadata(self, point_id: str, metadata: Dict[str, Any]) -> None:
        """
        Met à jour les métadonnées d'un point.
        
        Args:
            point_id (str): ID du point à mettre à jour
            metadata (Dict[str, Any]): Nouvelles métadonnées
        """
        # Récupérer le point actuel
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[point_id]
        )
        
        if not points:
            logger.error(f"Point avec ID {point_id} non trouvé")
            return
        
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
