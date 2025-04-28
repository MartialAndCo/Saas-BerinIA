from agents.base.base import AgentBase
from logs.agent_logger import log_agent
import datetime

class YouTubeScraperAgent(AgentBase):
    """
    Note: Cette classe est remplacée par la nouvelle implémentation plus complète 
    dans knowledge_injector_agent.py qui intègre à la fois Reddit et YouTube
    Conservée pour compatibilité avec le code existant.
    """
    def __init__(self):
        super().__init__("YouTubeScraperAgent")

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] ⚠️ DEPRECATED - Utiliser KnowledgeInjectorAgent dans knowledge_injector_agent.py")
        
        # Rediriger vers la nouvelle implémentation
        from agents.knowledge.knowledge_injector_agent import KnowledgeInjectorAgent
        
        # Adapter les paramètres pour la nouvelle interface
        knowledge_agent = KnowledgeInjectorAgent()
        
        # Si input_data contient déjà des paramètres de YouTube
        if "channels" in input_data or "keywords" in input_data:
            return knowledge_agent.extract_from_youtube(
                channels=input_data.get("channels"),
                keywords=input_data.get("keywords"),
                video_limit=input_data.get("video_limit", 10)
            )
        else:
            # Format générique
            youtube_data = {
                "source": "youtube",
                "type": "tutorial_insight",
                "data": input_data
            }
            return knowledge_agent.run(youtube_data)
