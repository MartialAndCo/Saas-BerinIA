#!/bin/bash
echo "Migration du scraper Apify vers la nouvelle implémentation..."
cd /root/infra-ia/agents/scraper/
mv apify_scraper.py apify_scraper_old.py
cp apify_client_scraper.py apify_scraper.py
sed -i '1i# Nouvelle implémentation renommée pour compatibilité\nfrom agents.scraper.apify_client_scraper import ApifyClientScraper as ApifyScraper\n# Le reste du fichier est conservé pour référence\n\n"""\nANCIENNE IMPLÉMENTATION - CONSERVÉE POUR RÉFÉRENCE\n"""\n' apify_scraper.py
echo "Migration terminée. L'ancienne implémentation a été conservée dans apify_scraper_old.py"
