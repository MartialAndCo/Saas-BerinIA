#!/usr/bin/env python3
"""
Test du système de stockage des campagnes.
"""

import json
import time
import datetime
import os
import sys

# Ajouter le chemin du projet pour l'importation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Démarrage du test de stockage des campagnes...")

# Importer notre nouveau module de stockage
try:
    from db.campaign_storage import (
        save_campaign, get_all_campaigns, get_campaign_by_id,
        get_campaigns_by_niche, get_active_campaigns, get_completed_campaigns
    )
    print("✅ Module de stockage de campagnes importé avec succès")
except ImportError as e:
    print(f"❌ Erreur lors de l'importation du module de stockage: {e}")
    sys.exit(1)

# Importer la fonction modifiée de postgres
try:
    from db.postgres import get_campaign_data
    print("✅ Module postgres importé avec succès")
except ImportError as e:
    print(f"❌ Erreur lors de l'importation du module postgres: {e}")
    sys.exit(1)

# Créer une campagne de test
def create_test_campaign(campaign_id=None, niche="Avocats", status="COMPLETED"):
    """Crée une campagne de test avec des données simulées."""
    if campaign_id is None:
        campaign_id = f"TEST-{int(time.time())}"
    
    return {
        "campaign_id": campaign_id,
        "niche": niche,
        "start_time": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
        "end_time": datetime.datetime.now().isoformat(),
        "status": status,
        "phases": {
            "scraping": {
                "status": "COMPLETED",
                "metrics": {
                    "leads_scraped": 20,
                    "time_taken": 5.3,
                    "sources": {
                        "apify": {
                            "leads_scraped": 0,
                            "time_taken": 0.5
                        },
                        "apollo": {
                            "leads_scraped": 20,
                            "time_taken": 4.8
                        }
                    }
                }
            },
            "cleaning": {
                "status": "COMPLETED",
                "metrics": {
                    "leads_cleaned": 18,
                    "leads_rejected": 2
                }
            },
            "classification": {
                "status": "COMPLETED",
                "metrics": {
                    "leads_classified": 18,
                    "hot_leads": 5,
                    "warm_leads": 8,
                    "cold_leads": 5
                }
            },
            "export": {
                "status": "COMPLETED",
                "metrics": {
                    "leads_exported": 10,
                    "leads_delayed": 8,
                    "export_strategy": "PAR_QUALITE"
                }
            },
            "contact": {
                "status": "COMPLETED",
                "metrics": {
                    "leads_contacted": 10,
                    "by_channel": {
                        "email": 7,
                        "phone": 3
                    }
                }
            }
        },
        "summary": {
            "leads_scraped": 20,
            "leads_cleaned": 18,
            "leads_classified": 18,
            "leads_exported": 10,
            "leads_contacted": 10
        }
    }

def test_save_and_retrieve():
    """Teste l'enregistrement et la récupération d'une campagne."""
    print("\n--- Test d'enregistrement et récupération ---")
    
    # Créer et sauvegarder une campagne
    campaign = create_test_campaign()
    campaign_id = campaign["campaign_id"]
    
    print(f"Sauvegarde de la campagne {campaign_id}...")
    success = save_campaign(campaign)
    
    if not success:
        print("❌ Échec de la sauvegarde")
        return False
    
    print(f"✅ Campagne {campaign_id} sauvegardée avec succès")
    
    # Récupérer la campagne par ID
    retrieved = get_campaign_by_id(campaign_id)
    
    if not retrieved:
        print(f"❌ Échec de la récupération de la campagne {campaign_id}")
        return False
    
    print(f"✅ Campagne {campaign_id} récupérée avec succès")
    print(f"  - Niche: {retrieved.get('niche')}")
    print(f"  - Leads scrapés: {retrieved.get('summary', {}).get('leads_scraped')}")
    
    return True

def test_multiple_campaigns():
    """Teste l'enregistrement et la récupération de plusieurs campagnes."""
    print("\n--- Test de plusieurs campagnes ---")
    
    # Créer et sauvegarder plusieurs campagnes avec différentes niches
    niches = ["Avocats", "Dentistes", "Architectes", "Consultants"]
    campaign_ids = []
    
    for i, niche in enumerate(niches):
        campaign = create_test_campaign(niche=niche)
        campaign_id = campaign["campaign_id"]
        campaign_ids.append(campaign_id)
        
        print(f"Sauvegarde de la campagne {i+1}/{len(niches)} ({niche})...")
        success = save_campaign(campaign)
        
        if not success:
            print(f"❌ Échec de la sauvegarde de la campagne {niche}")
            return False
    
    print(f"✅ {len(niches)} campagnes sauvegardées avec succès")
    
    # Récupérer toutes les campagnes
    all_campaigns = get_all_campaigns()
    print(f"Nombre total de campagnes: {len(all_campaigns)}")
    
    # Récupérer les campagnes par niche
    for niche in niches:
        niche_campaigns = get_campaigns_by_niche(niche)
        print(f"Campagnes pour la niche '{niche}': {len(niche_campaigns)}")
    
    return True

def test_active_campaigns():
    """Teste l'enregistrement et la récupération de campagnes actives."""
    print("\n--- Test des campagnes actives ---")
    
    # Créer et sauvegarder des campagnes actives
    active_statuses = ["IN_PROGRESS", "STARTING", "PAUSED"]
    campaign_ids = []
    
    for i, status in enumerate(active_statuses):
        campaign = create_test_campaign(status=status)
        campaign_id = campaign["campaign_id"]
        campaign_ids.append(campaign_id)
        
        print(f"Sauvegarde de la campagne active {i+1}/{len(active_statuses)} ({status})...")
        success = save_campaign(campaign)
        
        if not success:
            print(f"❌ Échec de la sauvegarde de la campagne {status}")
            return False
    
    print(f"✅ {len(active_statuses)} campagnes actives sauvegardées avec succès")
    
    # Récupérer les campagnes actives
    active_campaigns = get_active_campaigns()
    print(f"Nombre de campagnes actives: {len(active_campaigns)}")
    
    # Vérifier que chaque campagne active a bien été récupérée
    for campaign in active_campaigns:
        print(f"  - Campagne {campaign.get('campaign_id')}: {campaign.get('status')}")
    
    return True

def test_get_campaign_data():
    """Teste la fonction get_campaign_data de postgres.py."""
    print("\n--- Test de get_campaign_data ---")
    
    # Récupérer les campagnes passées et actives
    past_campaigns, active_campaigns = get_campaign_data()
    
    print(f"Nombre de campagnes passées: {len(past_campaigns)}")
    print(f"Nombre de campagnes actives: {len(active_campaigns)}")
    
    # Vérifier les campagnes passées
    if past_campaigns:
        print("Campagnes passées:")
        for i, campaign in enumerate(past_campaigns[:3]):  # Limiter à 3 pour ne pas submerger la console
            print(f"  {i+1}. {campaign.get('campaign_id')} - {campaign.get('niche')}")
    
    # Vérifier les campagnes actives
    if active_campaigns:
        print("Campagnes actives:")
        for i, campaign in enumerate(active_campaigns[:3]):  # Limiter à 3 pour ne pas submerger la console
            print(f"  {i+1}. {campaign.get('campaign_id')} - {campaign.get('niche')} - {campaign.get('status')}")
    
    return True

def main():
    """Fonction principale du test."""
    print("=== TEST DU SYSTÈME DE STOCKAGE DES CAMPAGNES ===")
    
    # Vérifier si le fichier de stockage existe
    storage_file = os.path.join("db", "campaigns.json")
    if os.path.exists(storage_file):
        print(f"Fichier de stockage trouvé: {storage_file}")
        try:
            with open(storage_file, "r") as f:
                data = json.load(f)
                print(f"Format du fichier: valide")
                print(f"Campagnes existantes: {len(data.get('campaigns', []))}")
                print(f"Dernière mise à jour: {data.get('last_updated', 'inconnue')}")
        except json.JSONDecodeError:
            print(f"Format du fichier: INVALIDE (JSON corrompu)")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")
    else:
        print(f"Fichier de stockage non trouvé (sera créé lors du premier test)")
    
    # Exécuter les tests
    tests = [
        ("Enregistrement et récupération", test_save_and_retrieve),
        ("Multiples campagnes", test_multiple_campaigns),
        ("Campagnes actives", test_active_campaigns),
        ("get_campaign_data", test_get_campaign_data)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n=== EXÉCUTION DU TEST: {name} ===")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Exception non gérée: {e}")
            results.append((name, False))
    
    # Afficher le résumé
    print("\n=== RÉSUMÉ DES TESTS ===")
    success_count = sum(1 for _, success in results if success)
    print(f"Tests réussis: {success_count}/{len(tests)}")
    
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status} - {name}")
    
    print("\n=== FIN DES TESTS ===")
    
    # Vérifier si le fichier de stockage existe maintenant
    if os.path.exists(storage_file):
        try:
            with open(storage_file, "r") as f:
                data = json.load(f)
                print(f"Fichier final: {len(data.get('campaigns', []))} campagnes stockées")
        except Exception:
            pass
    
    return 0 if all(success for _, success in results) else 1

if __name__ == "__main__":
    sys.exit(main())
