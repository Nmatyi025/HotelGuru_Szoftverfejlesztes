from marshmallow import Schema, fields, validate

from apiflask.validators import Email

class UserRequestSchema(Schema):
    name = fields.String()
    email = fields.Email(validate=Email())
    password = fields.String()
    phone = fields.String()

class UserResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.Email(validate=Email())
    phone = fields.String()

class UserLoginSchema(Schema):
    email = fields.Email(validate=Email())
    password = fields.String(required=True, validate=validate.Length(min=6))