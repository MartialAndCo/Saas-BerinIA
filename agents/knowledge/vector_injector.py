from agents.base.base import AgentBase
from logs.agent_logger import log_agent

class VectorInjectorAgent(AgentBase):
    """
    Note: Cette classe est remplacée par la nouvelle implémentation plus complète 
    dans knowledge_injector_agent.py qui gère l'extraction et l'injection
    Conservée pour compatibilité avec le code existant.
    """
    def __init__(self):
        super().__init__("VectorInjectorAgent")

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] ⚠️ DEPRECATED - Utiliser KnowledgeInjectorAgent dans knowledge_injector_agent.py")
        
        # Rediriger vers la nouvelle implémentation
        from agents.knowledge.knowledge_injector_agent import KnowledgeInjectorAgent
        
        # Adapter les paramètres pour la nouvelle interface
        knowledge_agent = KnowledgeInjectorAgent()
        
        # Pour l'injection directe de données vectorielles
        if "vectors" in input_data:
            # L'injection directe serait traitée par la méthode _inject_knowledge 
            # mais nous utilisons run() pour maintenir l'API publique cohérente
            knowledge_data = {
                "source": "direct_injection",
                "type": input_data.get("type", "manual_knowledge"),
                "data": {
                    "vectors": input_data.get("vectors", []),
                    "metadata": input_data.get("metadata", {})
                }
            }
            return knowledge_agent.run(knowledge_data)
        else:
            # Si les données ne sont pas déjà formatées en vecteurs,
            # transmettre telles quelles pour extraction + injection
            return knowledge_agent.run(input_data)
