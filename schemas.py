from marshmallow import Schema, fields
from marshmallow import pprint

from models import User

class BaseSchema(Schema):
    @classmethod
    def json(cls, obj):
        return cls().dump(obj)


class UserSchema(BaseSchema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
