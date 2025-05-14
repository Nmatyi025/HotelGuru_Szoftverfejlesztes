from marshmallow import Schema, fields, validate

class BaseRoomSchema(Schema):
    """Base schema for room-related data."""
    available = fields.Boolean()

class RoomsListSchema(BaseRoomSchema):
    """Schema for listing room details."""
    id = fields.Integer()
    room_number = fields.Integer()
    hotel_id = fields.Integer()
    price_per_night = fields.Float()
    description = fields.String(allow_none=True)

class RoomsResponseSchema(BaseRoomSchema):
    """Schema for room response data."""
    id = fields.Integer()
    room_number = fields.Integer()
    hotel_id = fields.Integer()
    price_per_night = fields.Float()
    description = fields.String(allow_none=True)
    photo_urls = fields.List(fields.String(), allow_none=True)
    available = fields.Boolean()

class RoomsRequestSchema(Schema):
    """Schema for creating or updating room details."""
    room_number = fields.Integer(required=True)
    hotel_id = fields.Integer(required=True)
    price_per_night = fields.Float(required=True)
    available = fields.Boolean()
    description = fields.String(allow_none=True)
    photo_urls = fields.List(fields.String(), allow_none=True)