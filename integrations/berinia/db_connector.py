"""
Module de connexion directe à la base de données Berinia.
Permet d'exporter les leads directement dans la DB Berinia.
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
import datetime
import json

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-db-connector")

# Configuration de la base de données
BERINIA_BACKEND_PATH = os.getenv("BERINIA_BACKEND_PATH", "/root/berinia/backend")
if BERINIA_BACKEND_PATH not in sys.path:
    sys.path.append(BERINIA_BACKEND_PATH)

# Charger les informations de connexion depuis le fichier .env de Berinia
BERINIA_ENV_PATH = os.path.join(BERINIA_BACKEND_PATH, ".env")
DB_URL = None

if os.path.exists(BERINIA_ENV_PATH):
    with open(BERINIA_ENV_PATH, "r") as env_file:
        for line in env_file:
            if line.strip().startswith("DATABASE_URL="):
                DB_URL = line.strip().split("=", 1)[1]
                break

if not DB_URL:
    # Valeurs par défaut si le fichier .env n'est pas trouvé
    DB_URL = "postgresql://berinia_user:password@localhost/berinia"

# Importer les modèles Berinia seulement si le chemin est valide
try:
    # Ajouter le répertoire de l'application au chemin Python
    from sqlalchemy import create_engine, text, insert
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.exc import SQLAlchemyError

    # Créer une connexion directe à la base de données
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Importer uniquement le modèle Lead pour éviter les dépendances circulaires
    try:
        from app.database.base_class import Base
        from app.schemas.lead import LeadCreate
        from app.models.lead import Lead
        from sqlalchemy.inspection import inspect
        
        # Vérifier si la table exists - evite les problèmes de mapper
        insp = inspect(engine)
        if insp.has_table("leads"):
            logger.info("✅ Table 'leads' trouvée dans la base de données Berinia")
            BERINIA_AVAILABLE = True
        else:
            logger.error("❌ Table 'leads' non trouvée - connexion à Berinia impossible")
            BERINIA_AVAILABLE = False
            
    except ImportError as e:
        logger.error(f"❌ Impossible d'importer les modèles Berinia: {str(e)}")
        BERINIA_AVAILABLE = False
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des tables: {str(e)}")
        BERINIA_AVAILABLE = False
    
    # Masquer le mot de passe dans les logs
    masked_url = DB_URL.split("@")
    if len(masked_url) > 1:
        credentials = masked_url[0].split("://")[1].split(":")
        if len(credentials) > 1:
            masked_url[0] = f"{masked_url[0].split('://')[0]}://{credentials[0]}:***"
        masked_url = "@".join(masked_url)
    else:
        masked_url = DB_URL
    
    logger.info(f"✅ Connexion à la DB Berinia réussie avec URL: {masked_url}")
except ImportError as e:
    BERINIA_AVAILABLE = False
    logger.error(f"❌ Impossible d'importer les modules Berinia: {str(e)}")
except Exception as e:
    BERINIA_AVAILABLE = False
    logger.error(f"❌ Erreur lors de la configuration de Berinia: {str(e)}")

def create_campaign_in_berinia(campaign_name: str, description: str = "") -> Optional[int]:
    """
    Crée une nouvelle campagne dans la base de données Berinia
    
    Args:
        campaign_name: Nom de la campagne à créer
        description: Description optionnelle de la campagne
        
    Returns:
        ID de la campagne créée ou None en cas d'erreur
    """
    if not BERINIA_AVAILABLE:
        logger.error("❌ Création de campagne impossible - Berinia non disponible")
        return None
        
    try:
        with SessionLocal() as db:
            # Insertion directe d'une nouvelle campagne
            stmt = text("""
                INSERT INTO campaigns (nom, description, date_creation, statut, target_leads, agent, niche_id) 
                VALUES (:nom, :description, :date_creation, :statut, :target_leads, :agent, :niche_id)
                RETURNING id
            """)
            
            # Utiliser la première niche disponible (ou créer une si nécessaire)
            try:
                niche_result = db.execute(text("SELECT id FROM niches LIMIT 1"))
                niche_id = niche_result.scalar()
                if not niche_id:
                    # Créer une niche par défaut si aucune n'existe
                    db.execute(text("INSERT INTO niches (nom, description) VALUES ('Default', 'Default niche for testing')"))
                    db.commit()
                    niche_id = 1
            except Exception as ne:
                logger.error(f"❌ Erreur lors de la récupération des niches: {str(ne)}")
                niche_id = 1  # Fallback

            params = {
                "nom": campaign_name,
                "description": description,
                "date_creation": datetime.datetime.now(),
                "statut": "active",
                "target_leads": 100,
                "agent": "CRMExporterAgent",
                "niche_id": niche_id
            }
            
            result = db.execute(stmt, params)
            campaign_id = result.scalar()
            db.commit()
            
            logger.info(f"✅ Campagne créée: {campaign_name} (ID: {campaign_id})")
            return campaign_id
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la campagne: {str(e)}")
        return None

def map_lead_to_berinia(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit un lead de notre format vers le format Berinia
    """
    # Mapper les champs
    email = lead.get("email", "")
    # S'assurer que l'email est valide ou utiliser une valeur explicitement factice
    if not email or "@" not in email:
        # Génération d'un email factice unique basé sur l'ID du lead ou d'autres propriétés uniques
        lead_id = lead.get("id", "")
        company = lead.get("company_name", "")
        phone = lead.get("phone", "")
        
        # Créer un hash unique basé sur les informations disponibles pour garantir l'unicité
        import hashlib
        unique_hash = hashlib.md5((lead_id + company + phone).encode()).hexdigest()[:8]
        
        # Email factice explicite UNIQUE pour satisfaire la validation sans confusion
        email = f"mail_{unique_hash}@emailfactice.com"
        logger.info(f"⚠️ Email manquant pour le lead: {lead.get('company_name', 'Inconnu')} - utilisation d'email factice unique: {email}")
    
    berinia_lead = {
        "nom": lead.get("contact_name") or lead.get("company_name", "Inconnu"),
        "email": email,
        "telephone": lead.get("phone", ""),
        "entreprise": lead.get("company_name", ""),
        "campagne_id": lead.get("campaign_id") if isinstance(lead.get("campaign_id"), int) else None,
        "statut": "new",
        "date_creation": datetime.datetime.now()
    }
    
    # Si le lead a un champ 'statut', l'utiliser
    if "status" in lead:
        berinia_lead["statut"] = lead["status"]
        
    return berinia_lead

def export_leads_to_berinia(leads: List[Dict[str, Any]], campaign_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Exporte une liste de leads vers la base de données Berinia
    
    Args:
        leads: Liste de leads à exporter
        campaign_id: ID optionnel de la campagne (si non spécifié dans les leads)
        
    Returns:
        Dict contenant les résultats de l'exportation
    """
    if not BERINIA_AVAILABLE:
        logger.error("❌ Export impossible - Berinia non disponible")
        return {
            "success": False, 
            "leads_count": 0,
            "message": "Export impossible - Berinia non disponible",
            "errors": ["Base de données Berinia non accessible ou non configurée"],
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    try:
        # Établir une connexion à la base de données
        with SessionLocal() as db:
            exported_count = 0
            errors = []
            exported_leads = []
            
            for lead in leads:
                try:
                    # Créer une nouvelle connexion pour chaque lead pour isoler les transactions
                    with SessionLocal() as lead_db:
                        # Mapper le lead au format Berinia
                        berinia_lead = map_lead_to_berinia(lead)
                        
                        # Si campaign_id est fourni et pas dans le lead, l'ajouter
                        if campaign_id is not None and not berinia_lead.get("campagne_id"):
                            berinia_lead["campagne_id"] = campaign_id
                        
                        # Vérifier qu'un ID de campagne est disponible
                        if not berinia_lead.get("campagne_id"):
                            raise ValueError("Aucun ID de campagne fourni - l'exportation nécessite une campagne valide")
                        
                        # Vérifier qu'au moins l'email OU le téléphone est disponible
                        if not berinia_lead["email"] and not berinia_lead["telephone"]:
                            raise ValueError("Le lead doit avoir au moins un email ou un numéro de téléphone valide")
                        
                        # Vérifier si le lead existe déjà (par téléphone ou email)
                        existing_lead = None
                        
                        # Vérification par téléphone prioritaire
                        if berinia_lead["telephone"]:
                            check_phone = lead_db.execute(
                                text("SELECT id FROM leads WHERE telephone = :telephone"),
                                {"telephone": berinia_lead["telephone"]}
                            ).fetchone()
                            if check_phone:
                                existing_lead = check_phone[0]
                                logger.info(f"Lead existant trouvé avec le téléphone {berinia_lead['telephone']} (ID: {existing_lead})")
                        
                        # Vérification par email seulement si c'est un vrai email (contient @) et pas un email généré
                        if not existing_lead and berinia_lead["email"] and "@" in berinia_lead["email"] and "domaine-inconnu.com" not in berinia_lead["email"]:
                            check_email = lead_db.execute(
                                text("SELECT id FROM leads WHERE email = :email"),
                                {"email": berinia_lead["email"]}
                            ).fetchone()
                            if check_email:
                                existing_lead = check_email[0]
                                logger.info(f"Lead existant trouvé avec l'email {berinia_lead['email']} (ID: {existing_lead})")
                        
                        if existing_lead:
                            # Mettre à jour le lead existant
                            update_stmt = text("""
                                UPDATE leads
                                SET nom = :nom,
                                    email = CASE WHEN :email = '' THEN email ELSE :email END,
                                    telephone = CASE WHEN :telephone = '' THEN telephone ELSE :telephone END,
                                    entreprise = :entreprise,
                                    statut = :statut,
                                    campagne_id = :campagne_id
                                WHERE id = :id
                                RETURNING id
                            """)
                            
                            params = {
                                "id": existing_lead,
                                "nom": berinia_lead["nom"],
                                "email": berinia_lead["email"],
                                "telephone": berinia_lead["telephone"],
                                "entreprise": berinia_lead["entreprise"],
                                "statut": berinia_lead["statut"],
                                "campagne_id": berinia_lead.get("campagne_id")
                            }
                            
                            result = lead_db.execute(update_stmt, params)
                            new_id = result.scalar()
                            lead_db.commit()
                            logger.info(f"✅ Lead mis à jour: {berinia_lead['nom']} (ID Berinia: {new_id})")
                        else:
                            # Insertion d'un nouveau lead
                            insert_stmt = text("""
                                INSERT INTO leads (nom, email, telephone, entreprise, date_creation, statut, campagne_id) 
                                VALUES (:nom, :email, :telephone, :entreprise, :date_creation, :statut, :campagne_id)
                                RETURNING id
                            """)
                            
                            params = {
                                "nom": berinia_lead["nom"],
                                "email": berinia_lead["email"],
                                "telephone": berinia_lead["telephone"],
                                "entreprise": berinia_lead["entreprise"],
                                "date_creation": berinia_lead["date_creation"],
                                "statut": berinia_lead["statut"],
                                "campagne_id": berinia_lead.get("campagne_id")
                            }
                            
                            result = lead_db.execute(insert_stmt, params)
                            new_id = result.scalar()
                            lead_db.commit()
                            logger.info(f"✅ Nouveau lead inséré: {berinia_lead['nom']} (ID Berinia: {new_id})")
                    
                    exported_count += 1
                    exported_leads.append(lead.get("id"))
                    logger.info(f"✅ Lead exporté: {berinia_lead['nom']} (ID Berinia: {new_id})")
                    
                except Exception as e:
                    error_msg = f"Erreur lors de l'export du lead {lead.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            return {
                "success": exported_count > 0,
                "leads_count": exported_count,
                "total_attempted": len(leads),
                "error_count": len(errors),
                "errors": errors,
                "leads_exported": exported_leads,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la connexion à la DB Berinia: {str(e)}")
        return {
            "success": False,
            "leads_count": 0,
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

# Fonction pour tester la connexion
def test_berinia_connection() -> bool:
    """
    Teste la connexion à la base de données Berinia
    
    Returns:
        bool: True si la connexion est réussie
    """
    if not BERINIA_AVAILABLE:
        logger.error("❌ Test ignoré - Berinia non disponible")
        return False
        
    try:
        # Tester la connexion avec une requête SQL simple
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Connexion à la DB Berinia réussie")
                return True
            else:
                logger.error("❌ Test de connexion échoué")
                return False
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la DB Berinia: {str(e)}")
        return False

# Fonction pour obtenir toutes les campagnes disponibles
def get_all_campaigns() -> List[Dict[str, Any]]:
    """
    Obtient la liste de toutes les campagnes disponibles dans Berinia
    
    Returns:
        Liste de dictionnaires contenant les campagnes
    """
    if not BERINIA_AVAILABLE:
        logger.error("❌ Récupération des campagnes impossible - Berinia non disponible")
        return []
        
    try:
        with SessionLocal() as db:
            stmt = text("SELECT id, nom, description, statut FROM campaigns ORDER BY date_creation DESC")
            result = db.execute(stmt)
            campaigns = [
                {"id": row[0], "nom": row[1], "description": row[2], "statut": row[3]} 
                for row in result
            ]
            return campaigns
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des campagnes: {str(e)}")
        return []

if __name__ == "__main__":
    # Test si exécuté directement
    connection_ok = test_berinia_connection()
    print(f"Connexion Berinia: {'OK' if connection_ok else 'ÉCHEC'}")
    
    if connection_ok:
        # Test avec un lead factice
        test_lead = {
            "id": "test_direct_" + datetime.datetime.now().strftime("%H%M%S"),
            "company_name": "Entreprise Test Direct",
            "email": "test@example.com",
            "phone": "+33612345678",
            "campaign_id": None  # Pas de campagne spécifiée
        }
        
        result = export_leads_to_berinia([test_lead])
        print(f"Résultat de l'export test: {json.dumps(result, indent=2)}")
