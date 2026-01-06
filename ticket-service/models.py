from config import db
from sqlalchemy.sql import func
import enum

class TicketCategory(enum.Enum):
    VIP = "VIP"
    REGULAR = "REGULAR"
    EARLY_BIRD = "EARLY_BIRD"

class TicketStatus(enum.Enum):
    OPEN = "OPEN"
    SOLD_OUT = "SOLD_OUT"
    CLOSED = "CLOSED"

class TicketType(db.Model):
    __tablename__ = "ticket_types"

    id = db.Column(db.String(36), primary_key=True)
    event_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.Enum(TicketCategory), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quota = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
