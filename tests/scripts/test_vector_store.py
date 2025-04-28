#!/usr/bin/env python3
"""
Script de test pour la mémoire vectorielle utilisant Qdrant.
Vérifie que l'installation fonctionne correctement et que les embeddings sont créés.
"""

import os
import sys
import logging
from datetime import datetime
import time
import argparse

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vectorstore_test")

# Importer les modules nécessaires
try:
    from utils.vectorstore import VectorStore
    from utils.embeddings import get_model_embedding, batch_get_embeddings, cosine_similarity
    from utils.config import get_config
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def test_qdrant_connection():
    """Teste la connexion à Qdrant"""
    logger.info("Test de la connexion à Qdrant...")
    
    config = get_config()
    
    try:
        # Créer une collection temporaire pour le test
        test_collection = f"test_collection_{int(time.time())}"
        vector_store = VectorStore(
            collection_name=test_collection,
            host=config.qdrant_host,
            port=config.qdrant_port
        )
        
        # Récupérer les infos de la collection
        collection_info = vector_store.get_collection_info()
        
        if not collection_info:
            logger.error("❌ Échec de connexion à Qdrant")
            return False
        
        logger.info(f"✅ Connexion à Qdrant réussie, collection '{test_collection}' créée")
        logger.info(f"Info collection: {collection_info}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la connexion à Qdrant: {str(e)}")
        return False

def test_embeddings():
    """Teste la génération d'embeddings"""
    logger.info("Test de la génération d'embeddings...")
    
    test_text = "Ceci est un texte de test pour vérifier la génération d'embeddings."
    
    try:
        # Obtenir un embedding
        start_time = time.time()
        embedding = get_model_embedding(test_text)
        duration = time.time() - start_time
        
        if not embedding:
            logger.error("❌ Échec de la génération d'embedding")
            return False
        
        # Vérifier la dimension
        embedding_size = len(embedding)
        logger.info(f"✅ Embedding généré avec succès, dimension: {embedding_size}")
        logger.info(f"Temps de génération: {duration:.2f} secondes")
        
        # Si la dimension est 1536, c'est probablement le modèle OpenAI ada-002
        # Si c'est environ 384, c'est probablement un modèle local
        if embedding_size == 1536:
            logger.info("Le modèle utilisé semble être OpenAI ada-002")
        elif 300 <= embedding_size <= 768:
            logger.info("Le modèle utilisé semble être un modèle local (sentence-transformers)")
        else:
            logger.info("Dimension d'embedding non standard, vérifier l'implémentation")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération d'embedding: {str(e)}")
        return False

def test_vector_operations():
    """Teste les opérations vectorielles complètes"""
    logger.info("Test des opérations vectorielles complètes...")
    
    # Créer une collection pour le test
    test_collection = f"test_vector_ops_{int(time.time())}"
    try:
        vector_store = VectorStore(collection_name=test_collection)
        
        # Préparer des textes et métadonnées pour le test
        texts = [
            "Paris est la capitale de la France.",
            "Berlin est la capitale de l'Allemagne.",
            "Londres est la capitale de l'Angleterre.",
            "Madrid est la capitale de l'Espagne.",
            "Rome est la capitale de l'Italie."
        ]
        
        metadatas = [
            {"country": "France", "continent": "Europe", "population": 2.161},
            {"country": "Allemagne", "continent": "Europe", "population": 3.645},
            {"country": "Angleterre", "continent": "Europe", "population": 8.982},
            {"country": "Espagne", "continent": "Europe", "population": 3.223},
            {"country": "Italie", "continent": "Europe", "population": 2.873}
        ]
        
        # 1. Tester l'ajout de textes par lots
        logger.info("Ajout de textes par lots...")
        ids = vector_store.add_texts(texts, metadatas)
        
        if not ids or len(ids) != len(texts):
            logger.error(f"❌ Échec de l'ajout de textes: {len(ids) if ids else 0} ajoutés sur {len(texts)}")
            return False
        
        logger.info(f"✅ {len(ids)} textes ajoutés avec succès")
        
        # 2. Tester la recherche de similitudes
        logger.info("Recherche de textes similaires...")
        results = vector_store.search_similar("Quelle est la capitale de la France?", limit=2)
        
        if not results:
            logger.error("❌ Échec de la recherche de similitudes")
            return False
        
        logger.info(f"✅ Recherche de similitudes réussie, {len(results)} résultats trouvés")
        for i, result in enumerate(results):
            logger.info(f"  Résultat {i+1}: Score={result['score']:.4f}, Texte='{result['text']}'")
        
        # 3. Tester la mise à jour des métadonnées
        logger.info("Mise à jour des métadonnées...")
        updated = vector_store.update_metadata(ids[0], {"population": 2.175, "updated": True})
        
        if not updated:
            logger.error("❌ Échec de la mise à jour des métadonnées")
            return False
        
        logger.info("✅ Mise à jour des métadonnées réussie")
        
        # 4. Tester la suppression par ID
        logger.info("Suppression d'un point par ID...")
        deleted = vector_store.delete_by_ids([ids[0]])
        
        if not deleted:
            logger.error("❌ Échec de la suppression par ID")
            return False
        
        logger.info("✅ Suppression par ID réussie")
        
        # 5. Tester la suppression par filtre
        logger.info("Suppression par filtre...")
        deleted = vector_store.delete_by_filter({"must": {"key": "country", "match": {"value": "Italie"}}})
        
        if not deleted:
            logger.error("❌ Échec de la suppression par filtre")
            return False
        
        logger.info("✅ Suppression par filtre réussie")
        
        # 6. Vérifier les informations de la collection
        collection_info = vector_store.get_collection_info()
        logger.info(f"État final de la collection: {collection_info}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors des opérations vectorielles: {str(e)}")
        return False

def run_tests(args):
    """Exécute tous les tests"""
    results = {}
    
    # Tester la connexion à Qdrant
    results["qdrant_connection"] = test_qdrant_connection()
    
    # Tester les embeddings
    results["embeddings"] = test_embeddings()
    
    # Tester les opérations vectorielles
    if args.full:
        results["vector_operations"] = test_vector_operations()
    
    # Afficher le résumé
    logger.info("\n=== Résumé des tests ===")
    all_pass = True
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_pass = False
    
    # Conseils pour la configuration
    if not all_pass:
        logger.info("\n=== Conseils de dépannage ===")
        
        if not results.get("qdrant_connection", True):
            logger.info("- Vérifiez que Qdrant est installé et en cours d'exécution")
            logger.info("- Vérifiez les paramètres de connexion dans config/.env")
            logger.info("- Commande pour installer Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        
        if not results.get("embeddings", True):
            logger.info("- Vérifiez votre clé API OpenAI dans config/.env")
            logger.info("- Pour utiliser des embeddings locaux, installez sentence-transformers:")
            logger.info("  pip install sentence-transformers")
    
    return all_pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test de la mémoire vectorielle")
    parser.add_argument("--full", action="store_true", help="Exécuter tous les tests, y compris les opérations vectorielles")
    args = parser.parse_args()
    
    logger.info("=== Début des tests de la mémoire vectorielle ===")
    success = run_tests(args)
    
    if success:
        logger.info("Tous les tests ont réussi!")
        sys.exit(0)
    else:
        logger.error("Certains tests ont échoué.")
        sys.exit(1)
