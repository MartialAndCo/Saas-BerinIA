from sqlalchemy import create_engine, text
from app.core.config import settings

def update_niches():
    """Mettre à jour les niches existantes avec des données métriques."""
    # Connexion à la base de données
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    
    try:
        print("Mise à jour des niches existantes...")
        
        # Données pour chaque niche
        niches_data = [
            {"nom": "Immobilier", "statut": "Rentable", "campagnes": 2, "leads": 440, "taux_conversion": 7.8, "cout_par_lead": 1.85, "recommandation": "Continuer"},
            {"nom": "Juridique", "statut": "Rentable", "campagnes": 1, "leads": 215, "taux_conversion": 5.2, "cout_par_lead": 2.1, "recommandation": "Continuer"},
            {"nom": "Architecture", "statut": "Rentable", "campagnes": 1, "leads": 189, "taux_conversion": 9.1, "cout_par_lead": 1.65, "recommandation": "Développer"},
            {"nom": "Ressources Humaines", "statut": "En test", "campagnes": 1, "leads": 78, "taux_conversion": 3.2, "cout_par_lead": 3.45, "recommandation": "Optimiser"},
            {"nom": "Santé", "statut": "En test", "campagnes": 1, "leads": 156, "taux_conversion": 6.5, "cout_par_lead": 2.25, "recommandation": "Continuer"},
            {"nom": "Restauration", "statut": "En test", "campagnes": 1, "leads": 98, "taux_conversion": 4.8, "cout_par_lead": 2.75, "recommandation": "Optimiser"},
            {"nom": "Éducation", "statut": "Abandonnée", "campagnes": 1, "leads": 245, "taux_conversion": 2.3, "cout_par_lead": 4.85, "recommandation": "Pivoter"},
            {"nom": "Tourisme", "statut": "Abandonnée", "campagnes": 1, "leads": 45, "taux_conversion": 2.1, "cout_par_lead": 5.2, "recommandation": "Pivoter"}
        ]
        
        # Mettre à jour chaque niche
        for niche in niches_data:
            conn.execute(text("""
                UPDATE niches 
                SET statut = :statut,
                    campagnes = :campagnes,
                    leads = :leads,
                    taux_conversion = :taux_conversion,
                    cout_par_lead = :cout_par_lead,
                    recommandation = :recommandation
                WHERE nom = :nom
            """), niche)
        
        conn.commit()
        print("Niches mises à jour avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour des niches: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    update_niches() 