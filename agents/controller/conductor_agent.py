# agents/controller/conductor_agent.py

from agents.base.base import AgentBase
from agents.controller.strategy_agent import StrategyAgent
from agents.controller.planning_agent import PlanningAgent
from agents.scraper.apify_scraper import ScraperAgent
from agents.analytics.campaign_analytics import AnalyticsAgent
from agents.pivot.pivot_decider import PivotAgent
from agents.controller.memory_manager_agent import MemoryManagerAgent

class ConductorAgent(AgentBase):
    def __init__(self):
        super().__init__("ConductorAgent")

        # Initialisation des agents de haut niveau
        self.strategy = StrategyAgent()
        self.planner = PlanningAgent()
        self.scraper = ScraperAgent()
        self.analytics = AnalyticsAgent()
        self.pivot = PivotAgent()
        self.memory = MemoryManagerAgent()

    def run(self, input_data: dict = {}) -> dict:
        print(f"[{self.name}] 🚀 Démarrage de l’orchestration...")

        # 1. Choisir une niche ou un secteur à cibler
        strategy_result = self.strategy.run({})
        niche = strategy_result.get("niche")
        print(f"🧠 Niche ciblée : {niche}")

        # 2. Vérifier si une exécution est planifiée
        planning = self.planner.run({"niche": niche})
        if not planning.get("planned"):
            return {"status": "skipped", "reason": "Non planifié pour cette niche."}

        # 3. Scraper les données liées à cette niche
        scraped = self.scraper.run({"niche": niche})
        print(f"🕸️ Données brutes récupérées : {scraped.get('data', [])[:2]}...")

        # 4. Analyse des résultats
        analysis = self.analytics.run({"data": scraped})
        print(f"📊 Résultat analytique : {analysis}")

        # 5. Décision de continuer, ajuster ou stopper
        decision = self.pivot.run({"analytics": analysis})
        print(f"⚖️ Décision : {decision}")

        # 6. Synchroniser la mémoire avec Qdrant si besoin
        memory_result = self.memory.run({"data": scraped})
        print(f"💾 Mémoire vectorielle mise à jour : {memory_result}")

        return {
            "status": "done",
            "niche": niche,
            "analysis": analysis,
            "decision": decision,
            "memory_sync": memory_result,
        }
