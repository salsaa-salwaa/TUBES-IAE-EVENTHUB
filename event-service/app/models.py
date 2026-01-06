import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    venue_id = Column(Integer, nullable=False)
    room_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    venue_capacity = Column(Integer, nullable=True, default=0)