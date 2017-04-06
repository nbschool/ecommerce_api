# from marshmallow import fields
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
    def json(cls, obj, include_data=None):
        """
        http://marshmallow.readthedocs.io/en/latest/quickstart.html#serializing-objects-dumping
        Serialize obj by passing it to schema's dump method, which returns
        the formatted result.

        :param obj object: The object to serialize
        :param include_data list: a list of fields inside the object to include
                                  inside the serialized response
        :returns: (data, errors)
        """
        if not include_data:
            serialized = cls().dump(obj)
        else:
            serialized = cls(include_data=include_data).dump(obj)

        return serialized.data, serialized.errors

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


class ItemSchema(BaseSchema):
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
    class Meta:
        type_ = 'order'
        self_url_many = '/orders/'

    id = fields.Str(dump_only=True, attribute='order_id')
    date = fields.DateTime()
    total_price = fields.Float()
    delivery_address = fields.Str()

    items = fields.Relationship(
        # related_url='/orders/{id}/items/',
        # related_url_kwargs={'id': '<order_id>'},
        many=True, include_resource_linkage=True,
        type_='item', schema=ItemSchema
    )

    @classmethod
    def json(cls, obj, include_data=['items']):
        """
        Override BaseSchema.json to automatically include the `items` field
        of the order.
        """
        return super(OrderSchema, cls).json(obj, include_data)


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

    orders = fields.Relationship(
        related_url='/users/{id}/orders',
        related_url_kwargs={'id': '<user_id>'},
        many=True, include_resource_linkage=True,
        type_='order', schema=OrderSchema
    )


def main():
    import uuid
    from datetime import datetime
    # User.delete().execute()
    Item.delete().execute()
    Order.delete().execute()
    OrderItem.delete().execute()

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
    orderitem1 = OrderItem.create(
        order=order1,
        item=item,
        quantity=2,
        subtotal=50.00
    )
    # orderitem2 = OrderItem.create(
    #     order=order1,
    #     item=item2,
    #     quantity=2,
    #     subtotal=50.00
    # )

    # print(OrderSchema.json(order1))

    # res = (
    #     Order
    #     .select(Order, OrderItem, Item)
    #     .join(OrderItem)
    #     .join(Item)
    #     .where(Order.order_id == order1.order_id)[0]
    # )
    order1.items = [item, item2]
    # pprint(order1.json())

    serialized, errors = OrderSchema.json(order1)

    print('Errors:', errors)
    print('\nData:')
    pprint(serialized)

    # # data for a test user
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "password": "antani",
        "email": "john.doe@email.com"
    }

    # # This simulates what needs to be present inside a POST/PUT request for the
    # # User endpoints, where `attributes` are the actual data needed to create
    # # the new user
    # post_data = {
    #     'data': {
    #         'type': 'user',
    #         'attributes': user_data
    #     }
    # }

    user = User(**user_data, user_id=uuid.uuid4())
    user.orders = [order1]
    # schema = UserSchema(user)

    # pprint('\nJSONSchema for User')
    # pprint(UserSchema.json_schema())

    # print('\nTest user peewee object json')
    # pprint(user.json())

    print('\nUserSchema for test user')
    pprint(UserSchema.json(user, include_data=['orders']))

    # print('\nUser jsonapi validation (True or dict with errors if any)')
    # pprint(UserSchema.validate_input(post_data))

    # print(OrderSchema.json_schema())

if __name__ == '__main__':
    main()
