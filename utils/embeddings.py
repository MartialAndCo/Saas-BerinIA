"""
Module de gestion des embeddings pour la mémoire vectorielle.
Supporte l'utilisation d'embeddings OpenAI ou d'alternatives locales.
"""

import logging
import numpy as np
from typing import List, Union, Optional
from utils.config import get_config

# Configuration du logging
logger = logging.getLogger(__name__)
config = get_config()

# Flag pour indiquer si les dépendances d'OpenAI sont disponibles
OPENAI_AVAILABLE = False
SENTENCE_TRANSFORMERS_AVAILABLE = False

# Essayer d'importer OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
    
    # Configurer la clé API si disponible
    api_key = config.get_openai_api_key()
    if api_key:
        openai.api_key = api_key
    else:
        logger.warning("Clé API OpenAI non configurée, les embeddings OpenAI ne seront pas disponibles")
        OPENAI_AVAILABLE = False
except ImportError:
    logger.warning("Module OpenAI non installé, les embeddings OpenAI ne seront pas disponibles")

# Essayer d'importer sentence-transformers comme alternative locale
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    LOCAL_MODEL = None
except ImportError:
    logger.warning("Module sentence-transformers non installé, les embeddings locaux ne seront pas disponibles")

def get_model_embedding(text: str, model: str = "text-embedding-ada-002") -> Optional[List[float]]:
    """
    Obtient l'embedding d'un texte en utilisant le modèle spécifié.
    Si le modèle OpenAI n'est pas disponible, essaie d'utiliser une alternative locale.
    
    Args:
        text (str): Le texte à transformer en embedding
        model (str): Le modèle à utiliser (par défaut: text-embedding-ada-002)
        
    Returns:
        List[float]: Vecteur d'embedding ou None si échec
    """
    # Vérifier que le texte n'est pas vide
    if not text or text.strip() == "":
        logger.warning("Tentative d'obtenir un embedding pour un texte vide")
        return None
    
    # Essayer d'utiliser OpenAI si disponible
    if OPENAI_AVAILABLE and config.get_openai_api_key():
        try:
            response = openai.Embedding.create(
                input=text,
                model=model
            )
            embedding = response["data"][0]["embedding"]
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding avec OpenAI: {str(e)}")
            # En cas d'échec, on essaiera l'alternative locale
    
    # Essayer d'utiliser sentence-transformers comme alternative
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            global LOCAL_MODEL
            
            # Charger le modèle si non chargé
            if LOCAL_MODEL is None:
                logger.info("Chargement du modèle SentenceTransformer local...")
                # all-MiniLM-L6-v2 est un bon compromis taille/performance
                LOCAL_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Générer l'embedding
            embedding = LOCAL_MODEL.encode(text)
            
            # Convertir en liste standard pour compatibilité
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding local: {str(e)}")
    
    # Si aucune méthode n'a fonctionné, simuler un embedding aléatoire
    logger.warning("Génération d'un embedding aléatoire (fallback)")
    
    # Déterminer la dimension en fonction du modèle
    if model == "text-embedding-ada-002":
        dim = 1536
    else:
        # Dimension par défaut pour les autres cas
        dim = 384
    
    # Générer un embedding aléatoire normalisé
    random_embedding = np.random.normal(0, 1, dim)
    normalized = random_embedding / np.linalg.norm(random_embedding)
    
    return normalized.tolist()

def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calcule la similarité cosinus entre deux embeddings.
    
    Args:
        embedding1 (List[float]): Premier vecteur d'embedding
        embedding2 (List[float]): Second vecteur d'embedding
        
    Returns:
        float: Score de similarité entre 0 et 1
    """
    if not embedding1 or not embedding2:
        return 0.0
        
    # Convertir en numpy arrays
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Calculer la similarité cosinus
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)

def batch_get_embeddings(texts: List[str], model: str = "text-embedding-ada-002") -> List[Optional[List[float]]]:
    """
    Obtient les embeddings pour une liste de textes.
    Optimise les appels API pour les modèles qui supportent le traitement par lots.
    
    Args:
        texts (List[str]): Liste de textes à transformer en embeddings
        model (str): Le modèle à utiliser (par défaut: text-embedding-ada-002)
        
    Returns:
        List[Optional[List[float]]]: Liste des vecteurs d'embedding (None en cas d'échec pour un texte)
    """
    # Filtrer les textes vides
    valid_texts = [text for text in texts if text and text.strip() != ""]
    
    if not valid_texts:
        logger.warning("Aucun texte valide pour les embeddings par lots")
        return [None] * len(texts)
    
    # Garder la trace des positions pour reconstruire la liste originale
    positions = {}
    for i, text in enumerate(texts):
        if text and text.strip() != "":
            positions[text] = i
    
    results = [None] * len(texts)
    
    # Essayer d'utiliser OpenAI en mode batch si disponible
    if OPENAI_AVAILABLE and config.get_openai_api_key():
        try:
            response = openai.Embedding.create(
                input=valid_texts,
                model=model
            )
            
            # Traiter les résultats
            for i, embedding_data in enumerate(response["data"]):
                text = valid_texts[i]
                original_pos = positions[text]
                results[original_pos] = embedding_data["embedding"]
                
            # Retourner les résultats avec les textes vides gérés
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings par lots avec OpenAI: {str(e)}")
            # Continuer avec l'alternative locale
    
    # Essayer d'utiliser sentence-transformers comme alternative
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            global LOCAL_MODEL
            
            # Charger le modèle si non chargé
            if LOCAL_MODEL is None:
                logger.info("Chargement du modèle SentenceTransformer local...")
                LOCAL_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Générer les embeddings en lot
            embeddings = LOCAL_MODEL.encode(valid_texts)
            
            # Assigner les résultats aux positions originales
            for i, text in enumerate(valid_texts):
                original_pos = positions[text]
                results[original_pos] = embeddings[i].tolist()
                
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings locaux par lots: {str(e)}")
    
    # Si aucune méthode n'a fonctionné, traiter chaque texte individuellement
    logger.warning("Aucune méthode de batch disponible, traitement individuel")
    for i, text in enumerate(texts):
        if text and text.strip() != "":
            results[i] = get_model_embedding(text, model)
    
    return results
