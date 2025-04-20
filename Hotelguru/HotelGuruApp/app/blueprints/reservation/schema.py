from marshmallow import Schema, fields
from apiflask.fields import Integer, String, Date

class ReservationRequestSchema(Schema):
    """Schema for creating a new reservation."""
    user_id = Integer(required=True)
    room_id = Integer(required=True)
    check_in = Date(required=True)
    check_out = Date(required=True)

class ReservationResponseSchema(Schema):
    """Schema for returning reservation details."""
    id = Integer()
    user_id = Integer()
    room_id = Integer()
    check_in = Date()
    check_out = Date()
    status = String()