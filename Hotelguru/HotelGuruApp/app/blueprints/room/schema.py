from marshmallow import Schema, fields, validate

class BaseRoomSchema(Schema):
    """Base schema for room-related data."""
    status = fields.Method("get_status")
    type = fields.Method("get_type")

    def get_status(self, obj):
        """Retrieve the status enum value as a string."""
        return obj.status.value if obj.status else None

    def get_type(self, obj):
        """Retrieve the type enum value as a string."""
        return obj.type.value if obj.type else None

class RoomsListSchema(BaseRoomSchema):
    """Schema for listing room details."""
    id = fields.Integer()
    name = fields.String()
    price = fields.Float()

class RoomsResponseSchema(BaseRoomSchema):
    """Schema for room response data."""
    name = fields.String()
    price = fields.Float()

class RoomsRequestSchema(Schema):
    """Schema for creating or updating room details."""
    name = fields.String()
    type = fields.String(required=True, validate=validate.OneOf(["single", "double", "suite"]))
    status = fields.String(required=True, validate=validate.OneOf(["available", "reserved", "maintenance"]))
    price = fields.Float()