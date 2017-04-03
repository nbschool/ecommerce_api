from marshmallow import Schema, fields
from marshmallow import pprint
from marshmallow_jsonschema import JSONSchema
from jsonschema.exceptions import ValidationError



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
        convert a marhsmallow object to a json
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
    """
    Schema for models.User
    """
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, loads_only=True)
