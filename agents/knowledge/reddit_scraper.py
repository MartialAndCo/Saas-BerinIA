from agents.base.base import AgentBase
from logs.agent_logger import log_agent
import datetime

class RedditScraperAgent(AgentBase):
    """
    Note: Cette classe est remplacée par la nouvelle implémentation plus complète 
    dans knowledge_injector_agent.py qui intègre à la fois Reddit et YouTube
    Conservée pour compatibilité avec le code existant.
    """
    def __init__(self):
        super().__init__("RedditScraperAgent")

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] ⚠️ DEPRECATED - Utiliser KnowledgeInjectorAgent dans knowledge_injector_agent.py")
        
        # Rediriger vers la nouvelle implémentation
        from agents.knowledge.knowledge_injector_agent import KnowledgeInjectorAgent
        
        # Adapter les paramètres pour la nouvelle interface
        knowledge_agent = KnowledgeInjectorAgent()
        
        # Si input_data contient déjà des paramètres de Reddit
        if "subreddits" in input_data:
            return knowledge_agent.extract_from_reddit(
                subreddits=input_data.get("subreddits"),
                time_period=input_data.get("time_period", "week"),
                post_limit=input_data.get("post_limit", 20)
            )
        else:
            # Format générique
            reddit_data = {
                "source": "reddit",
                "type": "community_insight",
                "data": input_data
            }
            return knowledge_agent.run(reddit_data)
