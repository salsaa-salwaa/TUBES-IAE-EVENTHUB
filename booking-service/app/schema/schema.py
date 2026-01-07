import graphene
from app.schema.booking_schema import (
    BookingType, 
    CreateBookingInput, 
    get_booking, 
    get_bookings_by_user, 
    create_booking, 
    CancelBooking,
    ConfirmPayment
)

class Query(graphene.ObjectType):
    booking = graphene.Field(BookingType, id=graphene.ID(required=True), resolver=get_booking)
    bookings_by_user = graphene.List(BookingType, user_id=graphene.ID(required=True), resolver=get_bookings_by_user)

class Mutation(graphene.ObjectType):
    create_booking = graphene.Field(BookingType, input=CreateBookingInput(required=True), resolver=create_booking)
    confirm_payment = ConfirmPayment.Field()
    cancel_booking = CancelBooking.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
