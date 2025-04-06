from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List
from apiflask.validators import Length, OneOf, Email
from app.models.user import User


class UserRequestSchema(Schema):
        
    name = fields.String()
    email = String(validate=Email())
    password = fields.String()
    phone = fields.String()


class UserResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    

class UserLoginSchema(Schema):
    email = String(validate=Email())
    password = fields.String()
    

class RoleSchema(Schema):
    id = fields.Integer()
    name = fields.String()