from agents.base.base import AgentBase
from logs.agent_logger import log_agent

class EmailSender(AgentBase):
    """
    Note: Cette classe est remplacée par la nouvelle implémentation plus complète 
    dans messenger_agent.py qui gère tous les canaux de communication
    Conservée pour compatibilité avec le code existant.
    """
    def __init__(self):
        super().__init__("EmailSenderAgent")
        
    def send_email(self, to_email, subject, body):
        """
        Simule l'envoi d'un email
        """
        print(f"[{self.name}] 📧 Simulation d'envoi d'email à {to_email}")
        print(f"[{self.name}] 📑 Sujet: {subject}")
        print(f"[{self.name}] 📄 Contenu: {body[:100]}...")
        
        # Pour la simulation, on considère que tous les emails sont envoyés avec succès
        return {
            "status": "sent",
            "message_id": f"email_{hash(to_email + subject) % 10000}",
            "recipient": to_email,
            "timestamp": "2025-04-25T20:30:00Z"
        }

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] ⚠️ DEPRECATED - Utiliser MessengerAgent dans messenger_agent.py")
        
        # Rediriger vers la nouvelle implémentation
        from agents.messenger.messenger_agent import MessengerAgent
        
        # Adapter les paramètres pour la nouvelle interface
        messenger_agent = MessengerAgent()
        
        # Formater les données pour forcer le canal Email
        if isinstance(input_data, dict):
            leads = input_data.get("leads", [])
            if not isinstance(leads, list):
                leads = [input_data]
                
            # Transformer les leads pour forcer l'utilisation du canal Email
            for lead in leads:
                lead["force_channel"] = "EMAIL"
            
            messenger_input = {
                "leads_to_contact": leads,
                "timezone": input_data.get("timezone", "Europe/Paris"),
                "email_response_rate": input_data.get("response_rate", 15),
                "force_email": True
            }
            
            return messenger_agent.run(messenger_input)
        else:
            return {"error": "Format d'entrée invalide", "email_sent": False}
