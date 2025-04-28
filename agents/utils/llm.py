import os
import openai
import time
from typing import Dict, Any, List, Optional
import logging

# Clé API depuis .env
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

def select_model(complexity: str = "standard") -> str:
    """
    Sélectionne le modèle LLM approprié en fonction du niveau de complexité requis.
    
    Args:
        complexity (str): Niveau de complexité ('nano', 'mini', 'standard')
        
    Returns:
        str: Nom du modèle à utiliser
    """
    models = {
        "nano": "gpt-4.1-nano",    # Tâches simples, rapides et peu coûteuses
        "mini": "gpt-4.1-mini",    # Bon équilibre performance/coût
        "standard": "gpt-4.1"      # Tâches complexes nécessitant des capacités avancées
    }
    return models.get(complexity, "gpt-4.1")

def ask_llm(
    prompt: str, 
    system_message: str = "Tu es un agent expert, logique, rigoureux, formel et stratégique.",
    model: str = "gpt-4.1",
    complexity: str = "standard",  # Nouveau paramètre pour sélectionner le modèle
    temperature: float = 0.5,
    max_tokens: int = 800,
    retry_count: int = 3,
    retry_delay: int = 5,
    json_mode: bool = False
) -> Dict[str, Any]:
    """
    Fonction centralisée améliorée pour interroger des modèles de langage.
    
    Args:
        prompt (str): Le prompt à envoyer au modèle
        system_message (str): Message système définissant le rôle du modèle
        model (str): Le modèle à utiliser
        temperature (float): Température de génération (0.0-1.0)
        max_tokens (int): Nombre maximal de tokens à générer
        retry_count (int): Nombre de tentatives en cas d'échec
        retry_delay (int): Délai entre les tentatives en secondes
        json_mode (bool): Forcer une réponse en format JSON
        
    Returns:
        Dict[str, Any]: La réponse du modèle, soit parsée comme JSON soit avec une clé 'text'
    """
    for attempt in range(retry_count):
        try:
            # Configuration des messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Configuration des paramètres
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Ajouter response_format si json_mode est activé (si supporté par le modèle)
            if json_mode and model in ["gpt-4-1", "gpt-4.1-mini"]:
                params["response_format"] = {"type": "json_object"}
            
            # Appel à l'API
            start_time = time.time()
            response = openai.ChatCompletion.create(**params)
            execution_time = time.time() - start_time
            
            # Log de la requête
            logger.info(f"LLM request completed in {execution_time:.2f}s using model {model}")
            
            # Traitement de la réponse
            content = response["choices"][0]["message"]["content"]
            
            # Si JSON mode est activé, on essaye de parser en JSON
            if json_mode:
                try:
                    import json
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, returning as text")
                    return {"text": content, "json_parse_error": True}
            else:
                # On essaie de parser en JSON si le contenu ressemble à du JSON
                if content.strip().startswith("{") and content.strip().endswith("}"):
                    try:
                        import json
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # Si échec, on retourne comme texte
                        return {"text": content}
                else:
                    return {"text": content}
                
        except Exception as e:
            logger.error(f"LLM request failed (attempt {attempt+1}/{retry_count}): {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(retry_delay)
            else:
                return {"error": str(e)}

def get_model_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Obtient l'embedding d'un texte à partir d'un modèle.
    
    Args:
        text (str): Le texte à convertir en embedding
        model (str): Le modèle d'embedding à utiliser
        
    Returns:
        List[float]: Le vecteur d'embedding
    """
    try:
        response = openai.Embedding.create(
            input=text,
            model=model
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Failed to get embedding: {str(e)}")
        return []

def generate_structured_response(
    prompt: str,
    schema: Dict[str, Any],
    system_message: str = "Tu es un agent expert qui génère des réponses structurées selon un schéma défini.",
    model: str = "gpt-4.1",
    complexity: str = "standard"
) -> Dict[str, Any]:
    """
    Génère une réponse structurée selon un schéma défini.
    
    Args:
        prompt (str): Le prompt à envoyer au modèle
        schema (Dict[str, Any]): Le schéma attendu pour la réponse
        system_message (str): Message système définissant le rôle du modèle
        model (str): Le modèle à utiliser
        
    Returns:
        Dict[str, Any]: La réponse structurée selon le schéma
    """
    # Création d'un prompt enrichi incluant le schéma
    enriched_prompt = f"""
    {prompt}
    
    Tu dois générer une réponse strictement au format JSON suivant ce schéma:
    ```json
    {schema}
    ```
    
    Réponds uniquement avec un objet JSON valide, sans texte supplémentaire.
    """
    
    return ask_llm(
        prompt=enriched_prompt,
        system_message=system_message,
        model=model,
        json_mode=True
    )
