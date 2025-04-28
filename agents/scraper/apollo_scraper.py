"""
Module de scraping utilisant Apollo.io pour extraire des leads B2B qualifiés.
"""

from agents.base.base import AgentBase
from logs.agent_logger import log_agent
import time
import random
import json
from datetime import datetime, timedelta

class ApolloScraper(AgentBase):
    """
    Agent qui utilise l'API Apollo.io pour extraire des leads professionnels
    hautement ciblés et qualifiés pour les campagnes B2B.
    NB: Pour l'instant, ce client simule les actions car nous n'avons pas d'API key.
    """
    def __init__(self, api_token=None):
        super().__init__("ApolloScraper")
        self.api_token = api_token
        print(f"[{self.name}] Initialisation du scraper Apollo (simulation)")
        
    def run(self, input_data: dict) -> dict:
        """
        Exécute le scraping Apollo selon les paramètres fournis
        
        Args:
            input_data: Dictionnaire contenant au minimum:
                - niche: La niche à scraper
                - filters: Filtres Apollo spécifiques (taille entreprise, industrie, etc.)
                - campaign_id: Identifiant de la campagne
                
        Returns:
            Dictionnaire contenant les leads extraits et métadonnées
        """
        print(f"[{self.name}] 🚀 Scraping Apollo pour la niche: {input_data.get('niche', 'N/A')}")
        
        # Extraire les paramètres
        niche = input_data.get("niche")
        filters = input_data.get("filters", {})
        campaign_id = input_data.get("campaign_id", "unknown")
        
        if not niche:
            result = {"error": "Aucune niche spécifiée", "leads": []}
            log_agent(self.name, input_data, result)
            return result
            
        # Ajouter des filtres par défaut si non spécifiés
        if not filters:
            filters = self._generate_default_filters(niche)
            
        # Simuler un temps de scraping (1-4 secondes)
        duration = random.uniform(1, 4)
        time.sleep(duration)
        
        # Simuler les leads extraits
        try:
            leads = self._simulate_apollo_leads(niche, filters)
            
            result = {
                "leads": leads,
                "count": len(leads),
                "niche": niche,
                "campaign_id": campaign_id,
                "time_taken": duration,
                "source": "apollo",
                "filters_used": filters,
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
    
    def _generate_default_filters(self, niche):
        """
        Génère des filtres Apollo par défaut adaptés à la niche.
        Dans Apollo, les filtres sont plus précis que dans Apify.
        """
        # Déterminer le secteur d'activité en fonction de la niche
        if "avocat" in niche.lower() or "juridique" in niche.lower() or "notaire" in niche.lower():
            industry = "Legal Services"
            employee_size_min = 1
            employee_size_max = 50
            job_titles = ["Partner", "Owner", "Managing Partner", "Attorney", "Lawyer"]
        elif "médecin" in niche.lower() or "santé" in niche.lower() or "cabinet médical" in niche.lower():
            industry = "Health, Wellness & Fitness"
            employee_size_min = 1
            employee_size_max = 30
            job_titles = ["Doctor", "Physician", "Practice Manager", "Office Manager", "Medical Director"]
        elif "immobil" in niche.lower() or "agence immobilière" in niche.lower():
            industry = "Real Estate"
            employee_size_min = 1
            employee_size_max = 50
            job_titles = ["Broker", "Agent", "Owner", "Agency Director", "Real Estate Manager"]
        elif "restaurant" in niche.lower() or "café" in niche.lower():
            industry = "Food & Beverages"
            employee_size_min = 5
            employee_size_max = 50
            job_titles = ["Owner", "Manager", "Restaurant Manager", "General Manager"]
        elif "comptable" in niche.lower() or "expert-comptable" in niche.lower():
            industry = "Accounting"
            employee_size_min = 1
            employee_size_max = 30
            job_titles = ["Accountant", "CPA", "Accounting Manager", "Partner", "Owner"]
        else:
            # Filtres génériques pour les autres niches
            industry = "Small Business"
            employee_size_min = 1
            employee_size_max = 100
            job_titles = ["Owner", "Founder", "CEO", "Director", "Manager"]
        
        # Construire les filtres
        return {
            "industry": industry,
            "employee_size": {
                "min": employee_size_min,
                "max": employee_size_max
            },
            "country": "France",
            "job_titles": job_titles,
            "seniority": ["Owner", "Executive", "Senior"],
            "keywords": niche.split(),
            "signal_scores": {
                "buying_intent": "high"
            },
            "recently_funded": False,
            "technologies": []
        }
    
    def _simulate_apollo_leads(self, niche, filters):
        """
        Simule des leads extraits d'Apollo pour une niche donnée.
        
        Apollo fournit généralement des leads de meilleure qualité,
        avec davantage d'informations professionnelles et de précision.
        """
        # Nombre de leads à simuler (entre 15 et 35)
        lead_count = random.randint(15, 35)
        
        # Pays francophones en Europe
        locations = {
            "France": ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Toulouse", "Nice", 
                      "Nantes", "Strasbourg", "Rennes", "Montpellier", "Grenoble"],
            "Belgium": ["Brussels", "Antwerp", "Ghent", "Charleroi", "Liège"],
            "Switzerland": ["Geneva", "Lausanne", "Zurich", "Bern", "Basel"]
        }
        
        # Liste de prénoms pour simulation
        first_names = ["Jean", "Marie", "Pierre", "Sophie", "Thomas", "Léa", "Paul", "Émilie", 
                       "Nicolas", "Céline", "Michel", "Nathalie", "David", "Julie"]
        
        # Liste de noms pour simulation
        last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", 
                      "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel"]
        
        # Générer les leads simulés
        leads = []
        for i in range(lead_count):
            # Prénom et nom aléatoires
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Sélectionner un pays et une ville aléatoirement
            country = random.choice(list(locations.keys()))
            city = random.choice(locations[country])
            
            # Déterminer le titre du poste en fonction des filtres
            job_title = random.choice(filters.get("job_titles", ["Owner"]))
            
            # Génération de nom d'entreprise en fonction de la niche
            if "avocat" in niche.lower() or "juridique" in niche.lower():
                company = f"Cabinet {last_name} & Associés"
                domain = f"cabinet-{last_name.lower()}.{country.lower() if country != 'France' else 'fr'}"
                industry = "Legal Services"
            elif "médecin" in niche.lower() or "santé" in niche.lower():
                company = f"Dr. {last_name} - Cabinet Médical"
                domain = f"docteur-{last_name.lower()}.{country.lower() if country != 'France' else 'fr'}"
                industry = "Health, Wellness & Fitness"
            elif "immobil" in niche.lower():
                company = f"Immobilier {last_name}"
                domain = f"immobilier-{last_name.lower()}.{country.lower() if country != 'France' else 'fr'}"
                industry = "Real Estate"
            else:
                company = f"{niche.capitalize()} {last_name}"
                domain = f"{niche.lower().replace(' ', '-')}-{last_name.lower()}.{country.lower() if country != 'France' else 'fr'}"
                industry = filters.get("industry", "Small Business")
            
            # Apollo a un taux élevé d'emails et téléphones valides
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            
            # Téléphone avec format international
            if country == "France":
                phone = f"+33{random.randint(600000000, 799999999)}"
            elif country == "Belgium":
                phone = f"+32{random.randint(400000000, 499999999)}"
            else:  # Switzerland
                phone = f"+41{random.randint(700000000, 799999999)}"
            
            # LinkedIn URL (Apollo spécialité)
            linkedin_url = f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}"
            
            # Signal de probabilité d'achat (spécifique à Apollo)
            buying_signals = random.choice(["low", "medium", "high"])
            
            # Taille de l'entreprise (nombre d'employés)
            employee_size = random.randint(
                filters.get("employee_size", {}).get("min", 1),
                filters.get("employee_size", {}).get("max", 50)
            )
            
            # Créer le lead avec le format Apollo
            lead = {
                "id": f"apollo_{int(time.time())}_{i}",
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "job_title": job_title,
                "seniority": random.choice(["Owner", "Executive", "Senior"]),
                "email": email,
                "email_status": random.choice(["verified", "verified", "verified", "unverified"]),  # 75% vérifié
                "phone": phone,
                "phone_status": random.choice(["verified", "verified", "unverified"]),  # 66% vérifié
                "company": {
                    "name": company,
                    "website": f"https://www.{domain}",
                    "industry": industry,
                    "size": employee_size,
                    "founded": random.randint(1980, 2020),
                    "linkedin_url": f"https://www.linkedin.com/company/{company.lower().replace(' ', '-')}"
                },
                "location": {
                    "country": country,
                    "city": city,
                    "continent": "Europe"
                },
                "social": {
                    "linkedin_url": linkedin_url,
                    "twitter_url": random.choice([None, f"https://twitter.com/{first_name.lower()}{last_name.lower()}"]),
                    "facebook_url": random.choice([None, None, f"https://facebook.com/{first_name.lower()}.{last_name.lower()}"]) # 33% chance
                },
                "buying_signals": buying_signals,
                "last_contacted": random.choice([None, None, None, (datetime.now() - timedelta(days=random.randint(30, 120))).isoformat()]),  # 25% chance
                "lead_source": "Apollo",
                "apollo_specific": {
                    "lead_score": random.randint(50, 95),
                    "intent_score": random.randint(30, 90),
                    "funding_round": None if random.random() > 0.05 else random.choice(["Seed", "Series A"]),  # 5% des leads
                    "account_stage": random.choice(["Prospect", "Target", "Lead", "Qualified"]),
                    "technologies": []
                },
                "scrape_date": datetime.now().isoformat()
            }
            
            leads.append(lead)
        
        return leads
