import graphene
import uuid
import requests
import json
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models.booking import Booking as BookingModel, PaymentStatus as StatusEnum
from app.config import settings
from datetime import datetime
from sqlalchemy import select

StatusEnumGraphene = graphene.Enum.from_enum(StatusEnum)

class BookingType(SQLAlchemyObjectType):
    class Meta:
        model = BookingModel
    
    status = StatusEnumGraphene()

class CreateBookingInput(graphene.InputObjectType):
    event_id = graphene.ID(required=True)
    ticket_type_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)

class Query(graphene.ObjectType):
    booking = graphene.Field(BookingType, id=graphene.ID(required=True))
    bookings_by_user = graphene.List(BookingType, user_id=graphene.ID(required=True))

    async def resolve_booking(self, info, id):
        session = info.context.get("db")
        result = await session.execute(select(BookingModel).filter_by(id=str(id)))
        return result.scalars().first()

    async def resolve_bookings_by_user(self, info, user_id):
        session = info.context.get("db")
        result = await session.execute(select(BookingModel).filter_by(user_id=str(user_id)))
        return result.scalars().all()

class CreateBooking(graphene.Mutation):
    class Arguments:
        input = CreateBookingInput(required=True)

    Output = BookingType

    async def mutate(self, info, input):
        user_id = info.context.get("user_id")
        session = info.context.get("db")
        
        if not user_id:
             raise Exception("Authentication Failed: User identity not found")

        event_query = """
        query ($id: ID!) {
            event(id: $id) {
                id
                title
                status
            }
        }
        """
        event_vars = {"id": str(input.event_id)}
        
        try:
            event_res = requests.post(
                settings.EVENT_SERVICE_URL,
                json={'query': event_query, 'variables': event_vars},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if event_res.status_code != 200:
                 raise Exception(f"Failed to connect to Event Service: {event_res.text}")
            
            event_data = event_res.json()
            if 'errors' in event_data:
                raise Exception(f"Event Service Error: {event_data['errors']}")
            
            event_obj = event_data['data']['event']
            if not event_obj:
                raise Exception(f"Event with ID {input.event_id} not found.")
            
            if event_obj['status'] != 'SCHEDULED':
                 raise Exception(f"Event '{event_obj['title']}' is not open for booking (Status: {event_obj['status']}). Only SCHEDULED events can be booked.")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Integration Error: Could not reach Event Service. {str(e)}")

        query = """
        query ($eventId: ID!) {
            ticketTypesByEvent(eventId: $eventId) {
                id
                price
                quota
                sold
            }
        }
        """
        variables = {"eventId": str(input.event_id)}
        
        try:
            response = requests.post(
                settings.TICKET_SERVICE_URL,
                json={'query': query, 'variables': variables},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to connect to Ticket Service: {response.text}")
                
            data = response.json()
            if 'errors' in data:
                raise Exception(f"Ticket Service Error: {data['errors']}")
            
            tickets = data['data']['ticketTypesByEvent']
            
            target_ticket = None
            for t in tickets:
                if str(t['id']) == str(input.ticket_type_id):
                    target_ticket = t
                    break
            
            if not target_ticket:
                raise Exception(f"Ticket Type ID '{input.ticket_type_id}' not found in this Event.")
                
            sold_count = target_ticket.get('sold', 0)
            if (target_ticket['quota'] - sold_count) < input.quantity:
                raise Exception(f"Quota insufficient. Remaining: {target_ticket['quota'] - sold_count}")
            
            total_price = target_ticket['price'] * input.quantity

            booking = BookingModel(
                event_id=str(input.event_id),
                user_id=str(user_id),
                ticket_type_id=str(input.ticket_type_id),
                quantity=input.quantity,
                total_price=float(total_price),
                status=StatusEnum.PENDING
            )
            
            session.add(booking)
            await session.commit()
            await session.refresh(booking)

            return booking

        except requests.exceptions.RequestException as e:
            raise Exception(f"Integration Error: Could not reach Ticket Service. {str(e)}")

class ConfirmPayment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    Output = BookingType

    async def mutate(self, info, id):
        user_id = info.context.get("user_id")
        session = info.context.get("db")
        
        if not user_id:
             raise Exception("Authentication Failed: User identity not found")

        result = await session.execute(select(BookingModel).filter_by(id=str(id)))
        booking = result.scalars().first()

        if not booking:
            raise Exception(f"Booking with ID {id} not found")

        if str(booking.user_id) != str(user_id):
            raise Exception("Unauthorized: You can only confirm your own bookings")

        if booking.status != StatusEnum.PENDING:
            raise Exception(f"Invalid status: Cannot confirm booking with status {booking.status}")

        update_query = """
        mutation ($id: ID!, $qty: Int!) {
            updateTicketSold(id: $id, quantity: $qty) {
                id
                sold
            }
        }
        """
        update_vars = {"id": str(booking.ticket_type_id), "qty": booking.quantity}
        
        try:
            quota_response = requests.post(
                settings.TICKET_SERVICE_URL, 
                json={'query': update_query, 'variables': update_vars},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if quota_response.status_code != 200:
                raise Exception(f"Failed to update ticket quota: {quota_response.text}")
            
            quota_data = quota_response.json()
            if 'errors' in quota_data:
                raise Exception(f"Ticket quota update failed: {quota_data['errors']}")
                
        except Exception as e:
            raise Exception(f"Confirmation failed - could not update ticket quota: {str(e)}")

        booking.status = StatusEnum.PAID
        await session.commit()
        await session.refresh(booking)

        return booking

async def get_booking(parent, info, id):
    session = info.context.get("db")
    result = await session.execute(select(BookingModel).filter_by(id=id))
    return result.scalars().first()

async def get_bookings_by_user(parent, info, user_id):
    session = info.context.get("db")
    result = await session.execute(select(BookingModel).filter_by(user_id=str(user_id)))
    return result.scalars().all()

async def create_booking(parent, info, input):
    mutation = CreateBooking()
    return await mutation.mutate(info, input)

async def cancel_booking(parent, info, id):
    session = info.context.get("db")
    result = await session.execute(select(BookingModel).filter_by(id=id))
    booking = result.scalars().first()
    if not booking:
        raise Exception(f"Booking with ID {id} not found")
    
    booking.status = StatusEnum.CANCELLED
    await session.commit()
    await session.refresh(booking)
    return booking

class Mutation(graphene.ObjectType):
    create_booking = CreateBooking.Field()
    confirm_payment = ConfirmPayment.Field()
    cancel_booking = graphene.Field(BookingType, id=graphene.ID(required=True), resolver=cancel_booking)

schema = graphene.Schema(query=Query, mutation=Mutation)
