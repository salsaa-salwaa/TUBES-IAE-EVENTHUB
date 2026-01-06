import graphene
import uuid
import requests
from models import TicketType as TicketModel, TicketCategory as CategoryEnum, TicketStatus as StatusEnum
from config import db
from auth import admin_required

CategoryEnumGraphene = graphene.Enum.from_enum(CategoryEnum)
StatusEnumGraphene = graphene.Enum.from_enum(StatusEnum)

class TicketType(graphene.ObjectType):
    id = graphene.ID()
    event_id = graphene.ID()
    name = CategoryEnumGraphene()
    price = graphene.Int()
    quota = graphene.Int()
    sold = graphene.Int()
    status = StatusEnumGraphene()

class CreateTicketInput(graphene.InputObjectType):
    event_id = graphene.ID(required=True)
    name = CategoryEnumGraphene(required=True)
    price = graphene.Int(required=True)
    quota = graphene.Int(required=True)

class UpdateTicketInput(graphene.InputObjectType):
    name = CategoryEnumGraphene()
    price = graphene.Int()
    quota = graphene.Int()
    status = StatusEnumGraphene()

class Query(graphene.ObjectType):
    ticket_types_by_event = graphene.List(
        TicketType,
        event_id=graphene.ID(required=True)
    )

    def resolve_ticket_types_by_event(self, info, event_id):
        return TicketModel.query.filter_by(event_id=str(event_id)).all()

    ticket_type = graphene.Field(TicketType, id=graphene.ID(required=True))

    def resolve_ticket_type(self, info, id):
        return TicketModel.query.filter_by(id=str(id)).first()

class CreateTicketType(graphene.Mutation):
    class Arguments:
        input = CreateTicketInput(required=True)

    Output = TicketType

    @admin_required
    def mutate(self, info, input):
        from config import EVENT_SERVICE_URL
        event_query = """
        query($id: ID!) {
          event(id: $id) {
            id
            venueCapacity
            status
          }
        }
        """
        venue_capacity = 0
        event_status = "SCHEDULED"

        try:
            res = requests.post(
                EVENT_SERVICE_URL,
                json={"query": event_query, "variables": {"id": str(input.event_id)}},
                timeout=5
            )
            res.raise_for_status()
            data = res.json()
            event_data = data.get("data", {}).get("event")
            if not event_data:
                raise Exception(f"Event with ID '{input.event_id}' not found in Event Service")
            
            venue_capacity = event_data.get("venueCapacity", 0)
            event_status = event_data.get("status", "SCHEDULED")

        except Exception as e:
            raise Exception(f"Failed to validate Event ID: {str(e)}")

        if event_status in ["COMPLETED", "CANCELLED"]:
            raise Exception(f"Cannot create tickets for event with status '{event_status}'")

        existing_tickets = TicketModel.query.filter_by(event_id=str(input.event_id)).all()
        total_quota_used = sum([t.quota for t in existing_tickets])

        if venue_capacity > 0:
            if (total_quota_used + input.quota) > venue_capacity:
                raise Exception(f"Total quota ({total_quota_used + input.quota}) exceeds venue capacity ({venue_capacity})")

        existing_ticket = TicketModel.query.filter_by(
            event_id=str(input.event_id),
            name=CategoryEnum(input.name)
        ).first()

        if existing_ticket:
            raise Exception(f"Ticket type '{input.name}' already exists for this event")

        if input.price < 0:
             raise Exception("Price cannot be negative")
        if input.quota < 0:
             raise Exception("Quota cannot be negative")

        ticket = TicketModel(
            id=str(uuid.uuid4()),
            event_id=str(input.event_id),
            name=CategoryEnum(input.name),
            price=input.price,
            quota=input.quota,
            sold=0,
            status=StatusEnum.OPEN
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

class DeleteTicketType(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @admin_required
    def mutate(self, info, id):
        ticket = TicketModel.query.filter_by(id=str(id)).first()
        if not ticket:
             raise Exception("Ticket not found")
        
        if ticket.sold > 0:
            raise Exception("Cannot delete ticket type that has been sold")
        
        db.session.delete(ticket)
        db.session.commit()
        return DeleteTicketType(ok=True)

class UpdateTicketType(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UpdateTicketInput(required=True)

    Output = TicketType

    @admin_required
    def mutate(self, info, id, input):
        ticket = TicketModel.query.filter_by(id=str(id)).first()
        if not ticket:
            raise Exception("Ticket type not found")
        
        if ticket.sold > 0:
            if input.price is not None and input.price != ticket.price:
                raise Exception("Cannot update price of ticket that has been sold")
            if input.name and CategoryEnum(input.name) != ticket.name:
                raise Exception("Cannot update name of ticket that has been sold")

        from config import EVENT_SERVICE_URL
        event_query = """
        query($id: ID!) {
          event(id: $id) {
            id
            status
            venueCapacity
          }
        }
        """
        venue_capacity = 0
        try:
            res = requests.post(
                EVENT_SERVICE_URL,
                json={"query": event_query, "variables": {"id": str(ticket.event_id)}},
                timeout=5
            )
            res.raise_for_status()
            data = res.json()
            event_data = data.get("data", {}).get("event", {})
            
            event_status = event_data.get("status", "SCHEDULED")
            venue_capacity = event_data.get("venueCapacity", 0)
            
            if event_status in ["COMPLETED", "CANCELLED"]:
                raise Exception(f"Cannot update tickets for event with status '{event_status}'")
                
        except Exception as e:
            raise Exception(f"Failed to validate Event Status/Capacity: {str(e)}")

        if input.name:
            ticket.name = CategoryEnum(input.name)
        if input.price is not None:
            if input.price < 0:
                 raise Exception("Price cannot be negative")
            ticket.price = input.price

        if input.quota is not None:
            if input.quota < 0:
                 raise Exception("Quota cannot be negative")
            if input.quota < ticket.sold:
                 raise Exception(f"Quota cannot be less than sold quantity ({ticket.sold})")
            
            if venue_capacity > 0:
                other_tickets = TicketModel.query.filter(
                    TicketModel.event_id == ticket.event_id,
                    TicketModel.id != ticket.id
                ).all()
                other_quota_used = sum([t.quota for t in other_tickets])
                
                if (other_quota_used + input.quota) > venue_capacity:
                    raise Exception(f"Total quota ({other_quota_used + input.quota}) exceeds venue capacity ({venue_capacity})")

            ticket.quota = input.quota
            
            if ticket.sold >= ticket.quota:
                ticket.status = StatusEnum.SOLD_OUT
            elif ticket.sold < ticket.quota and ticket.status == StatusEnum.SOLD_OUT:
                ticket.status = StatusEnum.OPEN

        if input.status:
            ticket.status = StatusEnum(input.status)
            
        db.session.commit()
        return ticket

class UpdateTicketSold(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    Output = TicketType

    def mutate(self, info, id, quantity):
        ticket = TicketModel.query.filter_by(id=str(id)).first()
        if not ticket:
            raise Exception("Ticket not found")
        
        if (ticket.quota - ticket.sold) < quantity:
             raise Exception(f"Not enough quota. Remaining: {ticket.quota - ticket.sold}")

        ticket.sold += quantity
        
        if ticket.sold >= ticket.quota:
            ticket.status = StatusEnum.SOLD_OUT
            
        db.session.commit()
        return ticket

class Mutation(graphene.ObjectType):
    create_ticket_type = CreateTicketType.Field()
    update_ticket_type = UpdateTicketType.Field()
    update_ticket_sold = UpdateTicketSold.Field()
    delete_ticket_type = DeleteTicketType.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
