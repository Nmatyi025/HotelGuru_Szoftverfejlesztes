from marshmallow import Schema, fields, validate

class BaseHotelSchema(Schema):
    """Base schema for hotel-related data."""
    available = fields.Boolean()

class HotelsListSchema(BaseHotelSchema):
    """Schema for listing hotel details."""
    id = fields.Integer()
    hotel_name = fields.String(required=True, validate=validate.Length(min=1))
    location = fields.String(required=True, validate=validate.Length(min=1))
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    description = fields.String(allow_none=True)
    photo_urls = fields.List(fields.String(), allow_none=True)

class HotelsResponseSchema(BaseHotelSchema):
    """Schema for hotel response data."""
    id = fields.Integer()
    hotel_name = fields.String(required=True, validate=validate.Length(min=1))
    location = fields.String(required=True, validate=validate.Length(min=1))
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    description = fields.String(allow_none=True)
    photo_urls = fields.List(fields.String(), allow_none=True)
    available = fields.Boolean()

class HotelsRequestSchema(Schema):
    """Schema for creating or updating hotel details."""
    hotel_name = fields.String(required=True, validate=validate.Length(min=1))
    location = fields.String(required=True, validate=validate.Length(min=1))
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    available = fields.Boolean()
    description = fields.String(allow_none=True)
    photo_urls = fields.List(fields.String(), allow_none=True)

