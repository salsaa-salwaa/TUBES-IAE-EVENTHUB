import graphene
from graphene import ObjectType, String, ID, List
from datetime import datetime
from app.database import SessionLocal
from app.models import Event
from app.constants import VALID_EVENT_STATUSES, EVENT_STATUS_SCHEDULED
import jwt
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-123")

def parse_datetime(value):
    try:
        if len(value) == 10:
            value += "T00:00:00"
        return datetime.fromisoformat(value.replace(" ", "T"))
    except ValueError:
        raise Exception("Invalid datetime format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM).")

def check_local_overlap(db, venue_id, room_id, start_dt, end_dt, exclude_id=None):
    """Cek apakah ada event lokal yang bentrok di venue & room yang sama"""
    query = db.query(Event).filter(
        Event.venue_id == venue_id,
        Event.room_id == room_id,
        Event.status != "CANCELLED"
    )
    
    if exclude_id:
        query = query.filter(Event.id != exclude_id)
        
    overlap = query.filter(
        Event.start_time < end_dt,
        Event.end_time > start_dt
    ).first()
    
    if overlap:
        raise Exception(
            f"Room ini already booked from {overlap.start_time} to {overlap.end_time} (Local)"
        )

class EventType(ObjectType):
    id = ID()
    title = String()
    description = String()
    venue_id = graphene.Int()
    room_id = graphene.Int()
    start_time = String()
    end_time = String()
    status = String()
    venue_capacity = graphene.Int()

    def resolve_start_time(self, info):
        if self.start_time:
            return self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def resolve_end_time(self, info):
        if self.end_time:
            return self.end_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

class Query(ObjectType):
    events = List(EventType)
    event = graphene.Field(EventType, id=ID(required=True))
    events_by_venue = List(EventType, venue_id=graphene.Int(required=True))

    def resolve_events(self, info):
        db = SessionLocal()
        return db.query(Event).all()

    def resolve_event(self, info, id):
        db = SessionLocal()
        return db.query(Event).filter(Event.id == id).first()

    def resolve_events_by_venue(self, info, venue_id):
        db = SessionLocal()
        return db.query(Event).filter(Event.venue_id == venue_id).all()

def get_token_payload(info):
    auth_header = info.context.headers.get("Authorization")
    if not auth_header:
        raise Exception("Authorization header missing")
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise Exception("Invalid authorization header format. Use 'Bearer <token>'")
    
    parts_1 = parts[1]
    
    try:
        return jwt.decode(parts_1, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


class CreateEvent(graphene.Mutation):
    class Arguments:
        title = String(required=True)
        description = String()
        venue_id = graphene.Int(required=True)
        room_id = graphene.Int(required=True)
        start_time = String(required=True)
        end_time = String(required=True)

    event = graphene.Field(EventType)

    def mutate(self, info, title, venue_id, room_id, start_time, end_time, description=None):
        payload = get_token_payload(info)

        if payload.get("role") != "ADMIN":
            raise Exception("Only admin can create event")

        db = SessionLocal()

        if not title.strip():
            raise Exception("Title cannot be empty")

        start_dt = parse_datetime(start_time)
        end_dt = parse_datetime(end_time)

        if start_dt >= end_dt:
            raise Exception("Start time must be before end time")

        from app.services.spacemaster_client import get_spacemaster_client
        spacemaster = get_spacemaster_client()
        
        try:
            validation_result = spacemaster.validate_venue_and_room(
                venue_id=venue_id,
                room_id=room_id,
                start_time=start_dt,
                end_time=end_dt
            )
            venue_capacity = validation_result.get("capacity", 0)
        except Exception as e:
            raise Exception(f"SpaceMaster validation failed: {str(e)}")

        check_local_overlap(db, venue_id, room_id, start_dt, end_dt)

        new_event = Event(
            title=title.strip(),
            description=description,
            venue_id=venue_id,
            room_id=room_id,
            start_time=start_dt,
            end_time=end_dt,
            status=EVENT_STATUS_SCHEDULED,
            venue_capacity=venue_capacity
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        try:
            result = spacemaster.block_schedule(
                room_id=room_id,
                start_time=start_dt,
                end_time=end_dt
            )
            res_data = result.get("blockSchedule", {})
            if not res_data.get("success"):
                raise Exception(f"SpaceMaster rejected booking: {res_data.get('message', 'No message')}")
        except Exception as e:
            raise Exception(f"Sync with SpaceMaster failed: {str(e)}")

        return CreateEvent(event=new_event)



class UpdateEvent(graphene.Mutation):
    class Arguments:
        id = ID(required=True)
        title = String()
        description = String()

    event = graphene.Field(EventType)

    def mutate(self, info, id, title=None, description=None):
        payload = get_token_payload(info)

        if payload.get("role") != "ADMIN":
            raise Exception("Only admin can update event")

        db = SessionLocal()

        event = db.query(Event).filter(Event.id == id).first()
        if not event:
            raise Exception("Event not found")

        if event.status == "COMPLETED":
            raise Exception("Completed event cannot be modified")

        if title is not None:
            if not title.strip():
                raise Exception("Title cannot be empty")
            event.title = title.strip()

        if description is not None:
            event.description = description

        db.commit()
        db.refresh(event)

        return UpdateEvent(event=event)

    


class BlockScheduleInput(graphene.InputObjectType):
    room_id = graphene.Int(required=True)
    start_time = graphene.String(required=True)
    end_time = graphene.String(required=True)

class BlockSchedule(graphene.Mutation):
    class Arguments:
        input = BlockScheduleInput(required=True)

    success = graphene.Boolean()
    message = String()

    def mutate(self, info, input):
        room_id = input.room_id
        start_time = input.start_time
        end_time = input.end_time
        start_dt = parse_datetime(start_time)
        end_dt = parse_datetime(end_time)

        from app.services.spacemaster_client import get_spacemaster_client
        spacemaster = get_spacemaster_client()
        
        db = SessionLocal()
        try:
            new_block = Event(
                title=f"Blocked via Proxy (Room {room_id})",
                description="Manual block triggered via direct blockSchedule mutation",
                venue_id=0, # Venue dummy karena blockSchedule cuma kirim roomId
                room_id=room_id,
                start_time=start_dt,
                end_time=end_dt,
                status="SCHEDULED"
            )
            db.add(new_block)
            db.commit()
        except Exception as e:
            db.rollback()
            pass

        try:
            result = spacemaster.block_schedule(
                room_id=room_id,
                start_time=start_dt,
                end_time=end_dt
            )
            data = result.get("blockSchedule", {})
            return BlockSchedule(
                success=data.get("success", True),
                message=data.get("message", "Success")
            )
        except Exception as e:
            raise Exception(f"SpaceMaster proxy error: {str(e)}")

class Mutation(ObjectType):
    create_event = CreateEvent.Field()
    update_event = UpdateEvent.Field()
    block_schedule = BlockSchedule.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
