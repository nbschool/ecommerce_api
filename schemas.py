from marshmallow_jsonapi import Schema, fields
from marshmallow import validate

import simplejson
"""
Validation rule to avoid empty strings.
Documentation can be found at https://goo.gl/pVvryk
"""
NOT_BLANK = validate.Length(min=1, error='Field cannot be blank')

"""Validation rule for prices that must be >= 0"""
MORE_THAN_ZERO = validate.Range(min=0)


class BaseSchema(Schema):
    """
    Base class for all Schemas.
    Extends marshmallow.Schema and Implements utility functions to validate
    inputs for the classes, to get schemas and serialize models data.
    """
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
    def validate_input(cls, jsondata):
        """"
        validate an input json data against the schema of its relative object
        schema

        documentation at https://goo.gl/0ZW1OW

        :returns:
        * True if validation is ok
        * Errors dict with validation errors if any
        """

        errors = cls().validate(jsondata)
        if not errors:
            return True, {}
        return False, errors


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
    name = fields.Str(validate=NOT_BLANK)
    price = fields.Float(validate=MORE_THAN_ZERO)
    description = fields.Str(validate=NOT_BLANK)
    availability = fields.Int(MORE_THAN_ZERO)


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

    id = fields.Str(dump_only=True, attribute='order_id')
    date = fields.DateTime(attribute='created_at', dump_only=True)
    total_price = fields.Decimal(dump_only=True, places=2,
                                 validate=MORE_THAN_ZERO)
    delivery_address = fields.Str(required=True, validate=NOT_BLANK)

    # Uses the OrderItem table and OrderItemSchema to serialize a json object
    # representing each item in the order
    items = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='item', schema='OrderItemSchema',
        dump_only=True, id_field='item.item_id',
        attribute='order_items',
    )

    user = fields.Relationship(
        include_resource_linkage=True,
        type_='user', schema='UserSchema',
        dump_only=True, id_field='user_id',
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
        self_url = '/items/{item_id}'
        self_url_kwargs = {'item_id': '<id>'}
        self_url_many = '/items/'

    id = fields.Str(dump_only=True, attribute='item.item_id')
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

    id = fields.Str(dump_only=True, attribute='user_id')
    first_name = fields.Str(required=True, validate=NOT_BLANK)
    last_name = fields.Str(required=True, validate=NOT_BLANK)
    email = fields.Email(required=True, validate=NOT_BLANK)
    password = fields.Str(required=True, validate=NOT_BLANK, load_only=True)

    orders = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='order', schema='OrderSchema',
        dump_only=True, id_field='order_id',
    )
