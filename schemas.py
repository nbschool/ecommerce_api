from marshmallow import pprint
from marshmallow_jsonschema import JSONSchema
from marshmallow_jsonapi import Schema, fields

from models import User, Item, Order, OrderItem


class BaseSchema(Schema):
    """
    Base class for all Schemas.
    Extends marshmallow.Schema and Implements utility functions to validate
    inputs for the classes, to get schemas and serialize models data.
    """
    @classmethod
    def json(cls, obj, include_data=[]):
        """
        http://marshmallow.readthedocs.io/en/latest/quickstart.html#serializing-objects-dumping
        Serialize obj by passing it to schema's dump method, which returns
        the formatted result.

        :param obj object: The object to serialize
        :param include_data list: a list of fields inside the object to include
                                  inside the serialized response
        :returns: (data, errors)
        """

        serialized = cls(include_data=include_data).dump(obj)
        return serialized.data, serialized.errors

    @classmethod
    def json_schema(cls):
        """"
        convert a marhsmallow object to a json schema
        TODO: This fails after adding `Relationship`s fields to schemas.
              Fix before usage.
        """

        # TODO: Remove after refactoring
        raise NotImplementedError('Refactor before using.')

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


class ItemSchema(BaseSchema):
    """
    Schema for models.Item.
    """

    class Meta:
        type_ = 'item'
        self_url = '/items/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/items/'

    id = fields.Str(dump_only=True, attribute='item_id')
    name = fields.Str()
    price = fields.Float()
    description = fields.Str()


class OrderSchema(BaseSchema):
    """
    Schema for models.Order.
    """

    class Meta:
        type_ = 'order'
        self_url_many = '/orders/'

    id = fields.Str(dump_only=True, attribute='order_id')
    date = fields.DateTime()
    total_price = fields.Float()
    delivery_address = fields.Str()

    items = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='item', schema=ItemSchema,
        dump_only=True
    )

    @classmethod
    def json(cls, obj, include_data=['items']):
        """
        Override BaseSchema.json to automatically include the `items` field
        of the order.
        """
        return super(OrderSchema, cls).json(obj, include_data)


class UserSchema(BaseSchema):
    """
    Schema for models.User
    """

    class Meta:
        type_ = 'user'
        self_url_many = '/users/'

    id = fields.Str(dump_only=True, attribute='user_id')
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    orders = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='order', schema=OrderSchema,
        dump_only=True
    )

    @classmethod
    def json(cls, obj, include_data=['orders']):
        """
        Override BaseSchema.json to automatically include the `orders` of
        the user.
        """
        return super(UserSchema, cls).json(obj, include_data)


def main():
    import uuid
    from datetime import datetime

    User.delete().execute()
    Item.delete().execute()
    Order.delete().execute()
    OrderItem.delete().execute()

    def print_serialized(data, errors):
        """
        Utility to print the result of a `BaseSchema.json()` call.
        """
        if errors:
            print('\nErrors:')
            pprint(errors)
        else:
            print('\nData:')
            pprint(data)

    # # data for a test user
    TEST_USER = {
        "first_name": "John",
        "last_name": "Doe",
        "password": "antani",
        "email": "john.doe@email.com"
    }
    TEST_ITEM = {
        'item_id': '429994bf-784e-47cc-a823-e0c394b823e8',
        'name': 'mario',
        'price': 20.20,
        'description': 'svariati mariii'
    }
    TEST_ITEM2 = {
        'item_id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
        'name': 'GINO',
        'price': 30.20,
        'description': 'svariati GINIIIII'
    }
    item = Item.create(**TEST_ITEM)
    item2 = Item.create(**TEST_ITEM2)

    order1 = Order.create(
        order_id=uuid.uuid4(),
        date=datetime.now(),
        total_price=100.00,
        delivery_address='Via Rossi 12'
    )

    order2 = Order.create(
        order_id=uuid.uuid4(),
        date=datetime.now(),
        total_price=50,
        delivery_address='Via Rossi 12'
    )

    user = User(**TEST_USER, user_id=uuid.uuid4())

    # Assign the items to the orders and the orders to the user inside a list,
    # so that the Schema can access and serialize the objects into a json
    # NOTE: This should be implemented as @property of the models.
    #       * User should have a property `orders` returning a list of orders
    #         created by the user
    #       * Orders should have
    #         * `items` that returns the list of items
    #         * `owner` (or similar) to retrieve the user that created it
    #       This could be achieved executing a query inside the property getter
    order1.items = [item, item2]
    order2.items = [item2, item]
    user.orders = [order1, order2]

    print('\nSerializing `order1` into JSONAPI with OrderSchema')
    print_serialized(*OrderSchema.json(order1))

    print('\nSerializing `user` into JSONAPI with UserSchema')
    print_serialized(*UserSchema.json(user))

    # This simulates what needs to be present inside a POST/PUT request for
    # the User endpoints, where `attributes` are the actual data needed to
    # create the new user
    post_data = {
        'data': {
            'type': 'user',
            'attributes': TEST_USER
        }
    }
    TEST_ITEM2 = {
        'item_id': '577ad826-a79d-41e9-a5b2-7955bcf03499',
        'name': 'GINO',
        'price': 30.20,
        'description': 'svariati GINIIIII'
    }
    item = Item.create(**TEST_ITEM)
    item2 = Item.create(**TEST_ITEM2)

    print('\nUser jsonapi validation (True or dict with errors if any)')
    pprint(UserSchema.validate_input(post_data))

    # # This simulates what needs to be present inside a POST/PUT request for the
    # # User endpoints, where `attributes` are the actual data needed to create
    # # the new user
    # post_data = {
    #     'data': {
    #         'type': 'user',
    #         'attributes': user_data
    #     }
    # }


if __name__ == '__main__':
    main()
