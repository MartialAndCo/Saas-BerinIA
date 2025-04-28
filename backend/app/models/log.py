from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database.base_class import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), index=True)
    message = Column(Text)
    source = Column(String(255))
    timestamp = Column(DateTime, default=func.now())
