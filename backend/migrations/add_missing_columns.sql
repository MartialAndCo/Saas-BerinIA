-- Ajouter les colonnes manquantes à la table agents
ALTER TABLE agents ADD COLUMN IF NOT EXISTS type VARCHAR;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS leads_generes INTEGER DEFAULT 0;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS campagnes_actives INTEGER DEFAULT 0;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS derniere_execution TIMESTAMP;

-- Ajouter les colonnes manquantes à la table campaigns
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS target_leads INTEGER DEFAULT 0;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS agent VARCHAR;

-- Ajouter la colonne entreprise à la table leads
ALTER TABLE leads ADD COLUMN IF NOT EXISTS entreprise VARCHAR; 