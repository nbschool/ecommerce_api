from marshmallow_jsonapi import Schema, fields


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
    name = fields.Str()
    price = fields.Float()
    description = fields.Str()


class OrderSchema(BaseSchema):
    """
    Schema for models.Order.
    Include an include relationship with the items included in the order and 
    the user that created it.
    """

    class Meta:
        type_ = 'order'
        self_url_many = '/orders/'

    id = fields.Str(dump_only=True, attribute='order_id')
    date = fields.DateTime(attribute='created_at')
    total_price = fields.Float()
    delivery_address = fields.Str()

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

    @classmethod
    def json(cls, obj, include_data=['items', 'user']):
        """
        Override BaseSchema.json to automatically include the `items` field
        of the order.
        """
        return super(OrderSchema, cls).json(obj, include_data)


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
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    orders = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='order', schema='OrderSchema',
        dump_only=True, id_field='order_id',
    )
