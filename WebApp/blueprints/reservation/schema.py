from marshmallow import Schema, fields
from apiflask.fields import Integer, String, Date, DateTime

class ReservationRequestSchema(Schema):
    """Schema for creating a new reservation."""
    user_id = Integer(required=True)
    room_id = Integer(required=True)
    start_date = Date(required=True)
    end_date = Date(required=True)
    status = String(required=True)

class ReservationResponseSchema(Schema):
    """Schema for returning reservation details."""
    id = Integer()
    user_id = Integer()
    room_id = Integer()
    start_date = Date()
    end_date = Date()
    status = String()
    created_on = DateTime()