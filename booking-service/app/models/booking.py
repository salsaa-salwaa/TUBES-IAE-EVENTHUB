from sqlalchemy import Column, Integer, String, Float, Enum as sqlEnum
import enum
from app.database import Base

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    ticket_type_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(sqlEnum(PaymentStatus), default=PaymentStatus.PENDING)
