from marshmallow import fields
from marshmallow import pprint
from marshmallow_jsonschema import JSONSchema
from marshmallow_jsonapi import Schema



class BaseSchema(Schema):
    """
    Base class for all Schemas.
    Extends marshmallow.Schema and Implements utility functions to validate
    inputs for the classes, to get schemas and serialize models data.
    """
    @classmethod
    def json(cls, obj):
        """
        http://marshmallow.readthedocs.io/en/latest/quickstart.html#serializing-objects-dumping
        Serialize obj by passing it to schema's dump method,
        which returns the formatted result
        """
        return cls().dump(obj).data

    @classmethod
    def json_schema(cls):
        """"
        convert a marhsmallow object to a json schema
        """
        return JSONSchema().dump(cls()).data

    @classmethod
    def validate_input(cls, jsondata):
        """"
        http://marshmallow.readthedocs.io/en/latest/quickstart.html#schema-validate
        validate an input json data against the schema of its relative object
        schema
        :returns:
        * True if validation is ok
        * Errors dict {<key>: <error>} if validation does not pass
        """
        errors = cls().validate(jsondata)
        if not errors:
            return True
        return errors


class UserSchema(BaseSchema):
    class Meta:
        type_ = 'user'
    """
    Schema for models.User
    """
    id = fields.Str(dump_only=True, attribute='user_id')
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    orders = fields.Relationship()


class OrderSchema(BaseSchema):
    class Meta:
        type_ = 'order'

        id = fields.Str(dump_only=True, attribute='order_id')
        date = fields.Date()
        total_price = fields.Decimal()
        quantiy = fields.Integer()
        subtotal = fields.Decimal()


def main():
    import uuid
    User.delete().execute()
    # data for a test user
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "password": "antani",
        "email": "john.doe@email.com"
    }

    # This simulates what needs to be present inside a POST/PUT request for the
    # User endpoints, where `attributes` are the actual data needed to create
    # the new user
    post_data = {
        'data': {
            'type': 'user',
            'attributes': user_data
        }
    }

    user = User(**user_data, user_id=uuid.uuid4())
    schema = UserSchema(user)

    pprint('\nJSONSchema for User')
    pprint(UserSchema.json_schema())

    print('\nTest user peewee object json')
    pprint(user.json())

    print('\nUserSchema for test user')
    pprint(UserSchema.json(user))

    print('\nUser jsonapi validation (True or dict with errors if any)')
    pprint(UserSchema.validate_input(post_data))


if __name__ == '__main__':
    main()
