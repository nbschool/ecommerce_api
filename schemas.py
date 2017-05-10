from marshmallow_jsonapi import Schema, fields
from marshmallow import validate

import simplejson
"""
Validation rule to avoid empty strings.
Documentation can be found at https://goo.gl/pVvryk
"""
NOT_BLANK = validate.Length(min=1, error='Field cannot be blank')

"""Validation rule for prices that must be >= 0 """
MORE_THAN_ZERO = validate.Range(min=0)
"""Validation rule for lists that cannot be empty. """
NOT_EMPTY = validate.Length(min=1, error='List cannot be empty')


class BaseSchema(Schema):
    """
    Base class for all Schemas.
    Extends marshmallow.Schema and Implements utility functions to validate
    inputs for the classes, to get schemas and serialize models data.
    """
    class Meta:
        json_module = simplejson

    @classmethod
    def jsonapi(cls, obj, include_data=[]):
        """
        Serialize obj by passing it to schema's dump method, which returns
        the formatted result.

        documentation at https://goo.gl/1GXhbR

        :param obj object: The object to serialize
        :param include_data list: a list of fields inside the object to include
                                  inside the serialized response
        :returns: (data, errors)
        """

        serialized = cls(include_data=include_data).dumps(obj)
        return serialized.data, serialized.errors

    @classmethod
    def jsonapi_list(cls, obj_list, include_data=[]):
        """
        Given a list of resource models returns a json array with all
        the rows of the table.
        return value is a string `[{resource}, ...]`
        """
        json_string = ','.join([o.json(include_data) for o in obj_list])
        json_string = '[{}]'.format(json_string)

        return json_string

    @classmethod
    def validate_input(cls, jsondata, partial=False):
        """"
        validate an input json data against the schema of its relative object
        schema

        documentation at https://goo.gl/0ZW1OW

        Returns `list` with errors (jsonapi standard) if any, else empty list
        """
        return cls().validate(jsondata, partial=partial)


class ItemSchema(BaseSchema):
    """
    Schema for models.Item.
    """

    class Meta:
        type_ = 'item'
        self_url = '/items/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/items/'

    id = fields.Str(dump_only=True, attribute='uuid')
    name = fields.Str(required=True, validate=NOT_BLANK)
    price = fields.Float(required=True, validate=MORE_THAN_ZERO)
    description = fields.Str(required=True, validate=NOT_BLANK)
    availability = fields.Int(required=True, validate=MORE_THAN_ZERO)


class OrderSchema(BaseSchema):
    """
    Schema for models.Order.
    Include an include relationship with the items included in the order and
    the user that created it.
    """

    class Meta:
        type_ = 'order'
        self_url_many = '/orders/'
        self_url = '/orders/{id}'
        self_url_kwargs = {'id': '<id>'}
        json_module = simplejson

    id = fields.Str(dump_only=True, attribute='uuid')
    date = fields.DateTime(attribute='created_at', dump_only=True)
    total_price = fields.Decimal(dump_only=True, places=2,
                                 validate=MORE_THAN_ZERO,
                                 )

    delivery_address = fields.Relationship(
        required=True, include_resource_linkage=True,
        type_='address', schema='AddressSchema',
        id_field='uuid',
    )

    # Uses the OrderItem table and OrderItemSchema to serialize a json object
    # representing each item in the order
    items = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='item', schema='OrderItemSchema',
        id_field='item.uuid',
        attribute='order_items', required=True,
        validate=NOT_EMPTY,
    )

    user = fields.Relationship(
        include_resource_linkage=True,
        type_='user', schema='UserSchema',
        id_field='uuid',
        required=True,
    )


class OrderItemSchema(BaseSchema):
    """
    Schema for representing OrderItem instances, uses data from the given
    OrderItem and its pointed Item to represent the relation between the
    Item and the Order that the OrderItem row links.

    Links generated from the Schema Meta class point to the Item resource.
    """

    class Meta:
        type_ = 'order_item'
        self_url = '/items/{uuid}'
        self_url_kwargs = {'uuid': '<id>'}
        self_url_many = '/items/'
        json_module = simplejson

    id = fields.Str(dump_only=True, attribute='item.uuid')
    name = fields.Str(attribute='item.name')
    description = fields.Str(attribute='item.description')
    price = fields.Float(attribute='item.price')
    quantity = fields.Int()
    subtotal = fields.Float()


class UserSchema(BaseSchema):
    """
    Schema for models.User, include relationship with user orders
    """

    class Meta:
        type_ = 'user'
        self_url_many = '/users/'
        self_url = '/users/{id}'
        self_url_kwargs = {'id': '<id>'}
        json_module = simplejson

    id = fields.Str(dump_only=True, attribute='uuid')
    first_name = fields.Str(required=True, validate=NOT_BLANK)
    last_name = fields.Str(required=True, validate=NOT_BLANK)
    email = fields.Email(required=True, validate=NOT_BLANK)
    password = fields.Str(required=True, validate=NOT_BLANK, load_only=True)
    admin = fields.Boolean(dump_only=True)

    orders = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='order', schema='OrderSchema',
        dump_only=True, id_field='uuid',
    )

    addresses = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='address', schema='AddressSchema',
        dump_only=True, id_field='uuid',
    )


class AddressSchema(BaseSchema):
    """
    Schema for models.Address
    """

    class Meta:
        type_ = 'address'
        self_url_many = '/addresses/'
        self_url = '/addresses/{id}'
        self_url_kwargs = {'id': '<id>'}
        json_module = simplejson

    id = fields.Str(dump_only=True, attribute='uuid')
    country = fields.Str(required=True, validate=NOT_BLANK)
    city = fields.Str(required=True, validate=NOT_BLANK)
    post_code = fields.Str(required=True, validate=NOT_BLANK)
    address = fields.Str(required=True, validate=NOT_BLANK)
    phone = fields.Str(required=True, validate=NOT_BLANK)

    user = fields.Relationship(
        include_resource_linkage=True,
        type_='user', schema='UserSchema',
        id_field='uuid', required=True,
    )
