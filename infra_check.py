import os
from db.postgres import get_connection
from memory.qdrant import ensure_collection_exists

def check_all():
    try:
        conn = get_connection()
        conn.close()
        print("✅ PostgreSQL : OK")
    except Exception as e:
        print("❌ PostgreSQL : KO →", str(e))

    try:
        res = ensure_collection_exists()
        print("✅ Qdrant : OK →", res)
    except Exception as e:
        print("❌ Qdrant : KO →", str(e))

if __name__ == "__main__":
    check_all()
