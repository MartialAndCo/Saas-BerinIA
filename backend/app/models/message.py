from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base_class import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    lead_name = Column(String)
    lead_email = Column(String)
    subject = Column(String)
    content = Column(Text)
    status = Column(String, default="sent")  # sent, delivered, opened, clicked, replied, bounced, failed
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign_name = Column(String)
    sent_date = Column(DateTime, default=datetime.utcnow)
    open_date = Column(DateTime, nullable=True)
    reply_date = Column(DateTime, nullable=True)

    # Relations
    lead = relationship("Lead", back_populates="messages")
    campaign = relationship("Campaign", back_populates="messages") 