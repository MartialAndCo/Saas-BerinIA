-- Créer la table messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    lead_name VARCHAR,
    lead_email VARCHAR,
    subject VARCHAR,
    content TEXT,
    status VARCHAR DEFAULT 'sent',
    campaign_id INTEGER REFERENCES campaigns(id),
    campaign_name VARCHAR,
    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    open_date TIMESTAMP,
    reply_date TIMESTAMP
);

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_messages_lead_id ON messages(lead_id);
CREATE INDEX IF NOT EXISTS idx_messages_campaign_id ON messages(campaign_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status); 