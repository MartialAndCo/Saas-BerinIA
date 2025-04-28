# Tests du système Infra-IA

Ce répertoire contient les tests et scripts de test pour le système Infra-IA.

## Structure

- `/tests` - Scripts de test principaux et utilitaires
  - `/tests/scripts` - Scripts de test spécifiques (test_analytics_agent.py, test_apify_client.py, etc.)
  - `/tests/reports` - Rapports générés par les tests
  - `/tests/logs` - Logs générés pendant l'exécution des tests
  - `/tests/data` - Données de test (résultats de scraping, données de migration, etc.)

## Scripts principaux

- `test_full_system.py` - Test complet du système avec toutes les phases
- `scripts/test_analytics_agent.py` - Test spécifique de l'agent d'analyse
- `scripts/test_apify_scraper.py` - Test du scraper Apify
- `scripts/test_vector_store.py` - Test du stockage vectoriel

## Utilisation

Pour exécuter le test complet du système :

```bash
python3 tests/test_full_system.py --niche "restaurant" --location "Paris, France" --max-leads 10
```

Options disponibles :
- `--niche` : Niche à cibler (par défaut: "restaurant")
- `--location` : Localisation (par défaut: "Paris, France")
- `--language` : Langue (par défaut: "fr")
- `--max-leads` : Nombre max de leads à scraper (par défaut: 10)
- `--max-export` : Limite quotidienne d'export (par défaut: 5)
- `--individual` : Tester chaque agent individuellement
- `--analytics` : Exécuter l'analyse post-campagne
- `--force-api` : Forcer l'utilisation des API réelles

Les rapports des tests seront générés dans le répertoire `tests/reports`.
