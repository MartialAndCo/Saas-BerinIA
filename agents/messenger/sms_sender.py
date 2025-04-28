from agents.base.base import AgentBase
from logs.agent_logger import log_agent

class SMSSender(AgentBase):
    """
    Module pour l'envoi de SMS.
    Note: Cette classe est remplacée par la nouvelle implémentation plus complète
    dans messenger_agent.py qui gère tous les canaux de communication.
    Conservée pour compatibilité avec le code existant.
    """
    def __init__(self):
        super().__init__("SMSSenderAgent")
        
    def send_sms(self, to_phone, message):
        """
        Simule l'envoi d'un SMS
        """
        print(f"[{self.name}] 📱 Simulation d'envoi de SMS à {to_phone}")
        print(f"[{self.name}] 📄 Contenu: {message}")
        
        # Pour la simulation, on considère que tous les SMS sont envoyés avec succès
        return {
            "status": "sent",
            "message_id": f"sms_{hash(to_phone + message) % 10000}",
            "recipient": to_phone,
            "timestamp": "2025-04-25T20:30:00Z"
        }
        
    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] ⚠️ DEPRECATED - Utiliser MessengerAgent dans messenger_agent.py")
        
        # Rediriger vers la nouvelle implémentation
        from agents.messenger.messenger_agent import MessengerAgent
        
        # Adapter les paramètres pour la nouvelle interface
        messenger_agent = MessengerAgent()
        
        # Formater les données pour forcer le canal SMS
        if isinstance(input_data, dict):
            leads = input_data.get("leads", [])
            if not isinstance(leads, list):
                leads = [input_data]
                
            # Transformer les leads pour forcer l'utilisation du canal SMS
            for lead in leads:
                lead["force_channel"] = "SMS"
            
            messenger_input = {
                "leads_to_contact": leads,
                "timezone": input_data.get("timezone", "Europe/Paris"),
                "force_sms": True
            }
            
            return messenger_agent.run(messenger_input)
        else:
            return {"error": "Format d'entrée invalide", "sms_sent": False}
