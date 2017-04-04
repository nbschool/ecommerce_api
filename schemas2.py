from marshmallow import pprint
from marshmallow_jsonapi import Schema, fields
from models import User




class BaseSchema(Schema):
    """
    """
    @classmethod
    def json(cls, obj):
        return cls().dump(obj).data


class UserSchema(BaseSchema):
    id = fields.Str(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

    class Meta:
        type_ = 'users'
        strict = True


user = User(first_name="Monty", last_name="dsfdsf", email="montsdf@asdhon.org", password="ewrwer")

user_schema = UserSchema()
jsonapi = user_schema.dump(users).data
pprint(jsonapi)
