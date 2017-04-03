from marshmallow import Schema, fields
from marshmallow import pprint
from marshmallow_jsonschema import JSONSchema
from jsonschema.exceptions import ValidationError



class BaseSchema(Schema):
    @classmethod
    def json(cls, obj):
        """
        converte un oggetto complesso (User, ad esempio) in un oggetto serializzabile (marshmallow object), un json in pratica
        """
        return cls().dump(obj).data

    @classmethod
    def json_schema(cls):
        """"
        converte un marshmallow schemas in un JSON Schema
        """
        return JSONSchema().dump(cls()).data

    @classmethod
    def validate_input(cls, jsondata):
        """"
        valida il json con il suo schema
        """
        errors = cls().validate(jsondata)
        if not errors:
            return True
        return errors



class UserSchema(BaseSchema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
