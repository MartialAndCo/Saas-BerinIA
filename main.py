import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from pydantic import BaseModel

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv("config/.env")

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
client = QdrantClient(url=qdrant_url)

COLLECTION_NAME = "test-collection"
if not client.collection_exists(COLLECTION_NAME):
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print(f"✅ Collection '{COLLECTION_NAME}' créée.")
else:
    print(f"✅ Collection '{COLLECTION_NAME}' déjà existante.")

# 🎯 Schéma d’état minimal
class EchoState(BaseModel):
    message: str
    result: str | None = None

def echo_agent(state: EchoState) -> EchoState:
    print("📣 Agent exécuté avec :", state.message)
    return EchoState(message=state.message, result=f"Echo: {state.message}")

# ⚙️ Création du graphe avec schéma
workflow = StateGraph(state_schema=EchoState)
workflow.add_node("echo", echo_agent)
workflow.set_entry_point("echo")

graph = workflow.compile()

if __name__ == "__main__":
    result = graph.invoke(EchoState(message="Hello BerinIA!"))
    print("🎯 Résultat final :", result)
