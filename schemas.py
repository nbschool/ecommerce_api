"""
This module implements validation and output generation classes using
`Marshmallow JSONAPI <http://marshmallow-jsonapi.readthedocs.io/>`_, an extension for
`Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ that implements the
`JSONAPI Standard <http://jsonapi.org/>`_, as well as all the custom validation rules
used by the classes.

Schemas are used to represent our resource :any:`models` and to validate clients' requests
data when needed.

Each implemented schemas should inherit from :any:`schemas.BaseSchema`, that implements all the
logic required for them to work, while each indivual schemas declare the resource description.

While schemas could be used directly they are meant to be inside the related :any:`models` resource
class.

"""
from marshmallow_jsonapi import Schema, fields
from marshmallow import validate

import simplejson

#: Validation rule to avoid empty strings.
#: Documentation can be found at https://goo.gl/pVvryk
NOT_BLANK = validate.Length(min=1, error='Field cannot be blank')

#: Validation rule for values that must be  ``value >= 0``
MORE_THAN_ZERO = validate.Range(min=0)

#: Validation rule for lists that cannot be empty.
NOT_EMPTY = validate.Length(min=1, error='List cannot be empty')


class BaseSchema(Schema):
    """
    Base class for all Schemas.
    Extends ``marshmallow.Schema`` and implements methods to validate
    data that can be used to generate new :any:`models` resources, as well as
    methods to generate output in form of stringified json.
    """
    class Meta:
        json_module = simplejson

    @classmethod
    def jsonapi(cls, obj, include_data=[]):
        """
        Serialize obj by passing it to schema's dump method, which returns
        the formatted result.

        documentation for ``Schema.dumps`` at https://goo.gl/1GXhbR

        Args:
            obj (:mod:`models` instance): The object to serialize
            include_data (list, optional): a list of fields inside the object to include
                                           inside the serialized response
        Returns:
            (data, errors)

            * ``data``: json :any:`str` generated from the object and included data
            * ``errors``: errors that may have occurred during the dump
        """

        serialized = cls(include_data=include_data).dumps(obj)
        return serialized.data, serialized.errors

    @classmethod
    def jsonapi_list(cls, obj_list, include_data=[]):
        """
        Serialize a series of resource models - with any related data specified - into a
        json stringified list.

        Args:
            obj_list (iterable): An iterable of :any:`models` of the same type.
                Each ``obj`` **must** implements a ``json``.
            include_data (list): A list of :any:`str` describing the name of the
                resource field that have to be included, if present.

        Returns:
            str: json representing a list of resources in the form of
            ``[{resource}, ...]``
        """
        json_string = ','.join(o.json(include_data) for o in obj_list)
        json_string = '[{}]'.format(json_string)

        return json_string

    @classmethod
    def validate_input(cls, jsondata, partial=False):
        """"
        validate an json-like data structure against the schema and return the
        reslt in form of a list of errors.

        documentation at https://goo.gl/0ZW1OW

        Args:
            jsondata (dict or list(dict)): data structure to validate against the schema
            partial (bool): wether to ignore missing fields (even if required).
                Allows for validation on ``PATCH`` requests.

        Returns:
            list: with errors (jsonapi standard) if any, else empty list
        """
        return cls().validate(jsondata, partial=partial)


class ItemSchema(BaseSchema):
    """
    Schema describing the Item resources.
    Can include:

    * ``pictures``
    """

    class Meta:
        type_ = 'item'
        self_url = '/items/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/items/'

    #: :any:`UUID` Id field
    id = fields.Str(dump_only=True, attribute='uuid')
    #: str: Item's name
    name = fields.Str(required=True, validate=NOT_BLANK)
    #: float: Single item price
    price = fields.Float(required=True, validate=MORE_THAN_ZERO)
    #: str: Item's description
    description = fields.Str(required=True, validate=NOT_BLANK)
    #: int: Quantity of items of this type available in the store
    availability = fields.Int(required=True, validate=MORE_THAN_ZERO)
    category = fields.Str(required=True, validate=NOT_BLANK)

    #: Relationship fields pointing to a list of :any:`models.Picture` related to the
    #: Currently parsed `Item`. If included it will attach all the pictures information
    #: within the `included` attribute of the generated json.
    pictures = fields.Relationship(
        include_resource_linkage=True,
        type_='picture', schema='PictureSchema',
        id_field='uuid', many=True,
    )


class OrderSchema(BaseSchema):
    """
    Schema describing an Order resource.
    Can include:

    * ``user``: Author of the order
    * ``delivery_address``: Resource pointing to the selected delivery address
    * ``items``: the list of items selected for the order
    """

    class Meta:
        type_ = 'order'
        self_url_many = '/orders/'
        self_url = '/orders/{id}'
        self_url_kwargs = {'id': '<id>'}
        json_module = simplejson

    #: :any:`UUID`: Order's ID
    id = fields.Str(dump_only=True, attribute='uuid')
    #: :any:`datetime`: Order's creation date
    date = fields.DateTime(attribute='created_at', dump_only=True)
    #: :any:`decimal.Decimal`: Order's total price, if passed through validation should
    #: be at least equal to 0
    total_price = fields.Decimal(dump_only=True, places=2,
                                 validate=MORE_THAN_ZERO,
                                 )

    #: Relationship pointing to a :any:`models.Address` that should be `owned` by
    #: the order's author.
    delivery_address = fields.Relationship(
        required=True, include_resource_linkage=True,
        type_='address', schema='AddressSchema',
        id_field='uuid',
    )

    #: Relationship field for the list of `item` that are in the order.
    #: Objects in the relationship list is generated through the
    #: :any:`OrderItemSchema`. If passed while validating should not be empty.
    items = fields.Relationship(
        many=True, include_resource_linkage=True,
        type_='item', schema='OrderItemSchema',
        id_field='item.uuid',
        attribute='order_items', required=True,
        validate=NOT_EMPTY,
    )

    #: Relationship field pointing the the :any:`models.User` that created the Order.
    user = fields.Relationship(
        include_resource_linkage=True,
        type_='user', schema='UserSchema',
        id_field='uuid',
        required=True,
    )


class OrderItemSchema(BaseSchema):
    """
    Schema for representing OrderItem instances but pointing to the related ``Item``
    resources.

    The output generated by the schema takes values from :any:`models.OrderItem`
    - `quantity` and `subtotal` as well as from the related :any:`models.Item`
    to generate a consistent and complete data structure.

    Links generated from the Schema Meta class point to the Item resource, since
    that the :any:`models.OrderItem` does not have a direct resource.
    """

    class Meta:
        type_ = 'order_item'
        self_url = '/items/{uuid}'
        self_url_kwargs = {'uuid': '<id>'}
        self_url_many = '/items/'
        json_module = simplejson

    #: :any:`UUID`: ID of the related **Item**
    id = fields.Str(dump_only=True, attribute='item.uuid')
    #: str: Item's name
    name = fields.Str(attribute='item.name')
    #: str: Item's description
    description = fields.Str(attribute='item.description')
    #: float: Item's price
    price = fields.Float(attribute='item.price')
    #: int: Quantity of item's of this type included in the order
    quantity = fields.Int()
    #: float: Subtotal for all the items of this type in the order
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


class PictureSchema(BaseSchema):
    class Meta:
        type_ = 'picture'
        self_url = '/pictures/{id}'
        self_url_kwargs = {'id': '<id>'}
        json_module = simplejson

    id = fields.Str(dump_only=True, attribute='uuid')
    # TODO: Make extensions validation rule oneOf
    extension = fields.Str(required=True, validate=NOT_BLANK)
    filename = fields.Str(dump_only=True)

    item = fields.Relationship(
        include_resource_linkage=True,
        type_='item', schema='ItemSchema',
        id_field='uuid', required=True,
    )
