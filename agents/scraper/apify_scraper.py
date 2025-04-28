# Nouvelle implémentation renommée pour compatibilité
from agents.scraper.apify_client_scraper import ApifyClientScraper as ApifyScraper
# Le reste du fichier est conservé pour référence

"""
ANCIENNE IMPLÉMENTATION - CONSERVÉE POUR RÉFÉRENCE
"""

"""
Module de scraping utilisant Apify Client pour extraire des leads depuis diverses sources web.
Implémentation basée sur l'API officielle Apify.
"""

from agents.base.base import AgentBase
from logs.agent_logger import log_agent
from utils.config import get_config
import time
import random
import json
from datetime import datetime
import logging

# Import du client Apify officiel
try:
    from apify_client import ApifyClient
    APIFY_CLIENT_AVAILABLE = True
except ImportError:
    APIFY_CLIENT_AVAILABLE = False
    print("Module apify-client non installé. Utilisez pip install apify-client pour l'installer.")

logger = logging.getLogger(__name__)

# ID de l'acteur Google Maps Scraper
GOOGLE_MAPS_ACTOR_ID = "2Mdma1N6Fd0y3QEjR"

class ApifyClientScraper(AgentBase):
    """
    Agent qui utilise l'API Apify pour extraire des informations et des leads
    depuis diverses sources web, en utilisant la bibliothèque cliente officielle.
    """
    def __init__(self, api_token=None):
        super().__init__("ApifyClientScraper")
        
        # Utiliser la clé API fournie ou celle de la configuration
        config = get_config()
        self.api_token = api_token or config.get_apify_api_key()
        self.daily_limit = config.apify_daily_limit
        
        # Vérifier si le client Apify est disponible et configuré
        self.use_simulation = not APIFY_CLIENT_AVAILABLE or self.api_token is None
        
        if self.use_simulation:
            logger.warning("Client Apify non disponible ou clé API manquante, fonctionnement en mode simulation")
            print(f"[{self.name}] Initialisation du scraper Apify (SIMULATION)")
        else:
            # Initialiser le client Apify
            self.client = ApifyClient(self.api_token)
            logger.info(f"Initialisation du client Apify avec API key: {self.api_token[:4]}...")
            print(f"[{self.name}] Initialisation du scraper Apify avec API réelle")
        
    def run(self, input_data: dict) -> dict:
        """
        Exécute le scraping selon les paramètres fournis
        
        Args:
            input_data: Dictionnaire contenant au minimum:
                - niche: La niche à scraper
                - params: Paramètres optionnels de scraping
                - campaign_id: Identifiant de la campagne
                
        Returns:
            Dictionnaire contenant les leads extraits et métadonnées
        """
        print(f"[{self.name}] 🕸️ Scraping web pour la niche: {input_data.get('niche', 'N/A')}")
        
        # Extraire les paramètres
        niche = input_data.get("niche")
        params = input_data.get("params", {})
        campaign_id = input_data.get("campaign_id", "unknown")
        
        if not niche:
            result = {
                "error": "Aucune niche spécifiée", 
                "leads": [], 
                "status": "FAILED",
                "message": "Une niche valide est requise pour le scraping. Veuillez fournir une niche cible."
            }
            log_agent(self.name, input_data, result)
            return result
            
        # Simuler un temps de latence réseau minimal
        time.sleep(0.5)
        
        try:
            start_time = time.time()
            
            # Utiliser l'API réelle si disponible, sinon simuler
            if not self.use_simulation:
                logger.info(f"Utilisation de l'API Apify réelle pour la niche: {niche}")
                # Préparer les paramètres pour l'API Apify
                apify_params = self._prepare_apify_params(niche, params)
                
                # Lancer la tâche de scraping avec l'API Apify Client
                leads = self._run_apify_actor(apify_params)
                
                # Calculer la durée réelle
                duration = time.time() - start_time
            else:
                # Mode simulation
                logger.info(f"Mode simulation pour la niche: {niche}")
                leads = self._simulate_leads_for_niche(niche, params)
                duration = time.time() - start_time
            
            result = {
                "leads": leads,
                "count": len(leads),
                "niche": niche,
                "campaign_id": campaign_id,
                "time_taken": duration,
                "api_used": not self.use_simulation,
                "status": "COMPLETED"
            }
            
            # Enregistrer dans les logs
            log_agent(self.name, input_data, result)
            
            return result
            
        except Exception as e:
            result = {
                "error": str(e),
                "leads": [],
                "niche": niche,
                "campaign_id": campaign_id,
                "status": "FAILED"
            }
            log_agent(self.name, input_data, result)
            return result
    
    def _prepare_apify_params(self, niche, params=None):
        """
        Prépare les paramètres pour l'API Apify Google Maps Scraper
        
        Args:
            niche: La niche à scraper
            params: Paramètres optionnels de scraping
            
        Returns:
            dict: Paramètres formatés pour l'API Apify
        """
        if params is None:
            params = {}
            
        # Obtenir la localisation
        location = params.get("locationQuery", "Paris, France")
        
        # Paramètres par défaut pour Google Maps Scraper
        default_params = {
            "searchStringsArray": [niche],
            "locationQuery": location,
            "maxCrawledPlacesPerSearch": 50,
            "language": "fr",
            "skipClosedPlaces": False,
            "placeMinimumStars": "",
            "website": "allPlaces",
            "searchMatching": "all"
        }
        
        # Fusionner les paramètres par défaut avec les paramètres fournis
        apify_params = {**default_params, **params}
        
        # S'assurer que searchStringsArray est une liste et contient la niche
        if "searchStringsArray" not in params or not params["searchStringsArray"]:
            apify_params["searchStringsArray"] = [niche]
        elif niche not in params["searchStringsArray"]:
            # S'assurer que la niche est dans la liste
            if isinstance(apify_params["searchStringsArray"], list):
                if niche not in apify_params["searchStringsArray"]:
                    apify_params["searchStringsArray"].append(niche)
            else:
                apify_params["searchStringsArray"] = [niche]
            
        # Limiter le nombre de résultats pour respecter les quotas
        if "maxCrawledPlacesPerSearch" not in params:
            # Utiliser une valeur raisonnable pour éviter de consommer trop de crédits
            if self.daily_limit and self.daily_limit < 1000:
                apify_params["maxCrawledPlacesPerSearch"] = min(50, self.daily_limit // 10)
            else:
                apify_params["maxCrawledPlacesPerSearch"] = 50
                
        logger.info(f"Paramètres Apify préparés: {apify_params}")
        return apify_params
    
    def _run_apify_actor(self, params):
        """
        Exécute l'acteur Apify Google Maps Scraper et récupère les résultats
        
        Args:
            params: Paramètres pour l'API
            
        Returns:
            list: Liste des leads convertis
        """
        if self.use_simulation:
            logger.warning("Client Apify non disponible, impossible d'exécuter la requête")
            return []
            
        try:
            logger.info(f"Appel de l'API Apify avec les paramètres: {params}")
            
            # Exécuter l'acteur et attendre qu'il soit terminé
            run = self.client.actor(GOOGLE_MAPS_ACTOR_ID).call(run_input=params)
            
            if not run or "defaultDatasetId" not in run:
                logger.error("Échec de l'exécution de l'acteur Apify: Aucun dataset retourné")
                return []
                
            dataset_id = run["defaultDatasetId"]
            logger.info(f"Acteur Apify exécuté avec succès. Dataset ID: {dataset_id}")
            
            # Récupérer les résultats du dataset
            apify_results = []
            for item in self.client.dataset(dataset_id).iterate_items():
                apify_results.append(item)
                
            logger.info(f"Récupération de {len(apify_results)} résultats depuis Apify")
            
            # Convertir les résultats en leads
            leads = self._convert_apify_results_to_leads(apify_results, params.get("searchStringsArray", [""])[0])
            
            return leads
            
        except Exception as e:
            logger.error(f"Exception lors de l'exécution de l'acteur Apify: {str(e)}")
            return []

    def _convert_apify_results_to_leads(self, apify_results, niche):
        """
        Convertit les résultats Apify en leads structurés
        
        Args:
            apify_results: Liste des résultats bruts d'Apify
            niche: La niche du scraping
            
        Returns:
            list: Liste des leads structurés
        """
        leads = []
        
        if not apify_results:
            return leads
            
        logger.info(f"Conversion de {len(apify_results)} résultats Apify en leads")
        
        for i, place in enumerate(apify_results):
            try:
                # Extraire les informations pertinentes
                company_name = place.get("title", "")
                if not company_name:
                    continue
                
                # Construire un lead à partir des données Google Maps
                lead = {
                    "id": f"apify_{int(time.time())}_{i}",
                    "company_name": company_name,
                    "contact_name": None,  # Google Maps ne fournit pas ce détail
                    "position": None,
                    "email": None,
                    "phone": place.get("phoneNumber"),
                    "website": place.get("website"),
                    "address": place.get("address", ""),
                    "city": self._extract_city_from_address(place.get("address", "")),
                    "postal_code": self._extract_postal_code(place.get("address", "")),
                    "country": "France",  # À modifier selon la localisation
                    "rating": place.get("totalScore"),
                    "reviews_count": place.get("reviewsCount"),
                    "category": place.get("categories", []),
                    "opening_hours": place.get("openingHours", {}),
                    "source": "Google Maps",
                    "scrape_date": datetime.now().isoformat(),
                    "niche": niche,
                    "raw_data": {
                        "place_id": place.get("placeId", ""),
                        "url": place.get("url", ""),
                        "description": place.get("description", ""),
                        "verified": place.get("verified", False),
                        "location": {
                            "lat": place.get("latitude"),
                            "lng": place.get("longitude")
                        }
                    }
                }
                
                leads.append(lead)
            except Exception as e:
                logger.warning(f"Erreur lors de la conversion du résultat {i}: {str(e)}")
                continue
                
        logger.info(f"Conversion terminée, {len(leads)} leads extraits")
        return leads

    def _extract_city_from_address(self, address):
        """
        Extrait la ville d'une adresse
        
        Args:
            address: Adresse complète
            
        Returns:
            str: Ville extraite ou chaîne vide
        """
        if not address:
            return ""
            
        # Tenter d'extraire la ville (format probable: "... 75001 Paris, France")
        parts = address.split(",")
        if len(parts) >= 2:
            city_part = parts[-2].strip()
            # Si la partie contient un code postal, extraire juste la ville
            city_words = city_part.split()
            if len(city_words) >= 2 and city_words[0].isdigit() and len(city_words[0]) == 5:
                return " ".join(city_words[1:])
            return city_part
            
        return ""
    
    def _extract_postal_code(self, address):
        """
        Extrait le code postal d'une adresse
        
        Args:
            address: Adresse complète
            
        Returns:
            str: Code postal extrait ou chaîne vide
        """
        if not address:
            return ""
            
        # Rechercher un motif de 5 chiffres qui pourrait être un code postal français
        parts = address.split()
        for part in parts:
            if part.isdigit() and len(part) == 5:
                return part
                
        return ""

    def _simulate_leads_for_niche(self, niche, params=None):
        """
        Simule des leads extraits pour une niche donnée
        
        Dans une implémentation réelle, cette méthode appellerait l'API Apify
        avec les paramètres appropriés pour extraire de vrais leads.
        """
        if params is None:
            params = {}
            
        # Nombre de leads à simuler (entre 15 et 50)
        lead_count = params.get("lead_count", random.randint(15, 50))
        
        # Liste de prénoms pour simulation
        first_names = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Léa", "Paul", "Émilie", 
                       "Nicolas", "Céline", "Michel", "Nathalie", "David", "Julie"]
        
        # Liste de noms pour simulation
        last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", 
                      "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel"]
        
        # Localités pour simulation
        locations = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Toulouse", "Nice", 
                     "Nantes", "Strasbourg", "Rennes", "Montpellier", "Grenoble"]
        
        # Récupérer les paramètres de localisation
        location_query = params.get("locationQuery", "Paris, FR")
        if isinstance(locations, list) and len(locations) > 0:
            location = random.choice(locations)
        else:
            location = location_query.split(",")[0]  # Prendre la ville depuis locationQuery
        
        # Générer les leads simulés avec la localisation spécifiée
        leads = []
        for i in range(lead_count):
            # Prénom et nom aléatoires
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Générer un nom d'entreprise basé sur la niche
            if "avocat" in niche.lower():
                company = f"Cabinet {last_name} & Associés"
                domain = "cabinet-juridique"
            elif "médecin" in niche.lower() or "santé" in niche.lower():
                company = f"Dr. {last_name} - {niche}"
                domain = "clinique-sante"
            elif "restaurant" in niche.lower():
                company = f"Restaurant {first_name} {last_name}"
                domain = "resto"
            elif "immobil" in niche.lower():
                company = f"Agence {first_name} {last_name} Immobilier"
                domain = "immobilier"
            else:
                company = f"{niche.capitalize()} {last_name}"
                domain = niche.lower().replace(" ", "-")
            
            # Email (parfois incomplet pour tester le nettoyage)
            has_valid_email = random.random() > 0.2  # 80% ont un email valide
            if has_valid_email:
                email_type = random.choice(["pro", "personnel", "générique"])
                if email_type == "pro":
                    email = f"{first_name.lower()}.{last_name.lower()}@{domain}.fr"
                elif email_type == "personnel":
                    providers = ["gmail.com", "outlook.fr", "yahoo.fr", "orange.fr"]
                    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(providers)}"
                else:
                    email = f"contact@{domain}.fr"
            else:
                email = None
            
            # Téléphone (parfois incomplet pour tester le nettoyage)
            has_valid_phone = random.random() > 0.3  # 70% ont un téléphone valide
            if has_valid_phone:
                phone_type = random.choice(["fixe", "mobile"])
                if phone_type == "fixe":
                    phone = f"01{random.randint(10000000, 99999999)}"
                else:
                    phone = f"06{random.randint(10000000, 99999999)}"
            else:
                phone = None
            
            # Site web (parfois absent)
            has_website = random.random() > 0.4  # 60% ont un site web
            if has_website:
                website = f"https://www.{domain}-{last_name.lower()}.fr"
            else:
                website = None
            
            # Créer le lead
            lead = {
                "id": f"lead_{int(time.time())}_{i}",
                "company_name": company,
                "contact_name": f"{first_name} {last_name}",
                "position": random.choice(["Directeur", "Gérant", "Responsable", "Fondateur", "Associé"]),
                "email": email,
                "phone": phone,
                "website": website,
                "address": f"{random.randint(1, 150)} rue de {random.choice(['la Paix', 'la République', 'Paris', 'Marseille'])}",
                "city": location,
                "postal_code": f"{random.randint(10, 95)}000",
                "country": "France",
                "source": random.choice(["LinkedIn", "Google Maps", "Pages Jaunes", "Site Web", "Annuaire"]),
                "scrape_date": datetime.now().isoformat(),
                "raw_data": {
                    "description": f"Entreprise de {niche} basée à {location}, spécialisée dans les services aux professionnels."
                }
            }
            
            leads.append(lead)
        
        return leads
