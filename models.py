"""
Application ORM Models built with Peewee
"""
import datetime
from uuid import uuid4

from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField, BooleanField
from peewee import SqliteDatabase, DecimalField
from peewee import UUIDField, ForeignKeyField, IntegerField
from playhouse.signals import Model, post_delete, pre_delete

from exceptions import InsufficientAvailabilityException, WrongQuantity
from schemas import (ItemSchema, UserSchema, OrderSchema, OrderItemSchema,
                     BaseSchema, AddressSchema, PictureSchema)
from utils import remove_image


database = SqliteDatabase('database.db')


class BaseModel(Model):
    """
    BaseModel implements all the common logic for all the application models,
    Acting as interface for the ``_schema`` methods and implementing common
    fields and methods for each model.

    .. NOTE::
        All models **must** inherit from BaseModel to work properly.

    Attributes:
        created_at (:any:`datetime.datetime`): creation date of the resource.
        updated_at (:any:`datetime.datetime`): updated on every :any:`save` call.
        _schema (:mod:`schemas`): Private attribute that each class
            that extends ``BaseModel`` should override with a model-specifig schema
            that describe how the model is to be validated and parsed for output.

    """

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    _schema = BaseSchema

    def save(self, *args, **kwargs):
        """
        Overrides Peewee ``save`` method to automatically update
        ``updated_at`` time during save.
        """
        self.updated_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database

    @classmethod
    def json_list(cls, objs_list):
        """
        Transform a list of instances of callee class into a jsonapi string


        Args:
            objs_list (iterable): Model instances to serialize into a json list

        Return:
            string: jsonapi compliant list representation of all the given resources
        """
        return cls._schema.jsonapi_list(objs_list)

    def json(self, include_data=[]):
        """
        Interface for the class defined ``_schema`` that returns a JSONAPI compliant
        string representing the resource.

        .. NOTE::
            If overridden (while developing or for other reason) the method
            should always return a ``string``.

        Args:
            include_data (list): List of attribute names to be included

        Returns:
            string: JSONAPI representation of the resource, including optional
            included resources (if any requested and present)
        """
        parsed, errors = self._schema.jsonapi(self, include_data)
        return parsed

    @classmethod
    def validate_input(cls, data, partial=False):
        """
        Validate any python structure against the defined ``_schema`` for the class.

        Args:
            data (dict|list): The data to validate against the ``class._schema``
            partial(bool): Allows to validate partial data structure (missing fields
            will be ignored, useful to validate ``PATCH`` requests.)

        Return:
            ``list``, with errors if any, empty if validation passed
        """
        return cls._schema.validate_input(data, partial=partial)


class Item(BaseModel):
    """
    Item describes a product for the e-commerce platform.

    Attributes:
        uuid (UUID): Item UUID
        name (str): Name for the product
        price (decimal.Decimal): Price for a single product
        description (str): Product description
        availability (int): Quantity of items available
        category (str): Category group of the item

    """
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()
    availability = IntegerField()
    category = TextField()
    _schema = ItemSchema

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.uuid,
            self.name,
            self.price,
            self.description)


@database.atomic()
@pre_delete(sender=Item)
def on_delete_item_handler(model_class, instance):
    """Delete item pictures in cascade"""
    pictures = Picture.select().join(Item).where(
        Item.uuid == instance.uuid)
    for pic in pictures:
        pic.delete_instance()


class Picture(BaseModel):
    """
    A Picture model describes and points to a stored image file. Allows linkage
    between the image files and one :any:`Item` resource.

    Attributes:
        uuid (UUID): Picture's uuid
        extension (str): Extension of the image file the Picture's model refer to
        item (:any:`Item`): Foreign key referencing the Item related to the Picture.
            A ``pictures`` field can be used from ``Item`` to access the Item resource
            pictures
    """
    uuid = UUIDField(unique=True)
    extension = CharField()
    item = ForeignKeyField(Item, related_name='pictures')
    _schema = PictureSchema

    @property
    def filename(self):
        """Full name (uuid.ext) of the file that the Picture model reference."""
        return '{}.{}'.format(
            self.uuid,
            self.extension)

    def __str__(self):
        return '{}.{} -> item: {}'.format(
            self.uuid,
            self.extension,
            self.item.uuid)


@post_delete(sender=Picture)
def on_delete_picture_handler(model_class, instance):
    """Delete file picture"""
    # TODO log eventual inconsistency
    remove_image(instance.uuid, instance.extension)


class User(BaseModel, UserMixin):
    """
    User represents an user for the application.

    Attributes:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's **valid** email
        password (str): User's password
        admin (bool): User's admin status. Defaults to ``False``

    .. NOTE::
        Each User resource must have an unique `email` field, meaning
        that there cannot be two user's registered with the same email.

        For this reason, when checking for user's existence, the server requires
        either the `uuid` of the user or its `email`.
    """
    uuid = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)
    _schema = UserSchema

    @staticmethod
    def exists(email):
        """
        Check that an user exists by checking the email field.

        Args:
            email (str): User's email to check
        """
        try:
            User.get(User.email == email)
        except User.DoesNotExist:
            return False
        return True

    @staticmethod
    def hash_password(password):
        """
        Use passlib to get a crypted password.

        Args:
            password (str): password to hash

        Returns:
            str: hashed password
        """
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        """
        Verify a clear password against the stored hashed password of the user
        using passlib.

        Args:
            password (str): Password to verify against the hashed stored password
        Returns:
            bool: wether the given email matches the stored one
        """
        return pbkdf2_sha256.verify(password, self.password)


class Address(BaseModel):
    """
    The model Address represent a user address.
    Each address is releated to one user, but one user can have
    more addresses.

    Attributes:
        uuid (UUID): Address unique uuid
        user (:any:`User`): Foreign key pointing to the user `owner` of the address
        country (str): Country for the address, i.e. ``Italy``
        city (str): City name
        post_code (str): Postal code for the address
        address (str): Full address for the Address resource
        phone (str): Phone number for the Address
    """
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name='addresses')
    country = CharField()
    city = CharField()
    post_code = CharField()
    address = CharField()
    phone = CharField()

    _schema = AddressSchema


class Order(BaseModel):
    """
    Orders represent an order placed by a `User`, containing one or more `Item`
    that have to be delivered to one of the user's `Address`.

    Attributes:
        uuid (UUID): Order's unique id
        total_price (:any:`decimal.Decimal`): Total price for the order
        delivery_address (:any:`Address`): Address specified for delivery
        user (:any:`User`): User that created the order
    """
    uuid = UUIDField(unique=True, default=uuid4)
    total_price = DecimalField(default=0)
    delivery_address = ForeignKeyField(Address, related_name="orders")
    user = ForeignKeyField(User, related_name="orders")
    _schema = OrderSchema

    class Meta:
        order_by = ('created_at',)

    @property
    def order_items(self):
        """
        Property that execute a cross-table query against :class:`models.OrderItem`
        to get a list of all OrderItem related to the callee order.

        Returns:
            list: :class:`models.OrderItem` related to the order.
        """

        query = (
            OrderItem
            .select(OrderItem, Order)
            .join(Order)
            .where(Order.uuid == self.uuid)
        )

        return [orderitem for orderitem in query]

    def empty_order(self):
        """
        Remove all the items from the order deleting all OrderItem related
        to this order and resetting the order's total_price value to 0.

        Returns:
            Order: callee order instance
        """

        self.total_price = 0
        OrderItem.delete().where(OrderItem.order == self).execute()
        self.save()
        return self

    def add_item(self, item, quantity=1):
        """
        Add one item to the order.
        Creates one OrderItem row if the item is not present in the order yet,
        or increasing the count of the existing OrderItem. It also updates the
        item availability counter and raise InsufficientAvailability if
        quantity is less than item availability.

        Args:
            item (Item): The Item to be added
            quantity(int, optional): How many items to add
        Returns:
            Order: callee instance
        """
        for orderitem in self.order_items:
            # Looping all the OrderItem related to this order, if one with the
            # same item is found we update that row.
            if orderitem.item == item:
                orderitem.add_item(quantity)

                self.total_price += (item.price * quantity)
                self.save()
                return self

        # if no existing OrderItem is found with this order and this Item,
        # create a new row in the OrderItem table and use OrderItem.add_item
        # to properly use the calculus logic that handles updating prices and
        # availability. To use correctly add_item the initial quantity and
        # subtotal are set to 0
        OrderItem.create(
            order=self,
            item=item,
            quantity=0,
            subtotal=0,
        ).add_item(quantity)

        self.total_price += (item.price * quantity)
        self.save()

        return self

    def update_item(self, item, quantity):
        """
        Update the Order with the new quantity of the given item. Takes care
        of creating a new :class:`models.OrderItem` if needed or, adding or removing
        the correct quantity for an existing OrderItem.

        Args:
            item (Item): Item to update for this order
            quantity (int): **new** quantity for the item

        Returns:
            None

        """
        for order_item in self.order_items:
            if order_item.item == item:
                diff = quantity - order_item.quantity
                if diff > 0:
                    self.add_item(item, abs(diff))
                elif diff < 0:
                    self.remove_item(item, abs(diff))
                break
        else:
            self.add_item(item, quantity)

    def remove_item(self, item, quantity=1):
        """
        Remove the given item from the order, reducing quantity of the relative
        OrderItem entity or deleting it if removing the last item
        ``(OrderItem.quantity == 0)``.
        It also restores the item availability.

        Args:
            item (Item): Item to be removed
            quantity (int): How many item to remove

        Returns:
            Order: callee instance

        """
        for orderitem in self.order_items:
            if orderitem.item == item:
                removed_items = orderitem.remove_item(quantity)
                item.availability += quantity
                item.save()
                self.total_price -= (item.price * removed_items)
                self.save()
                return self

        # No OrderItem found for this item
        # TODO: Raise or return something more explicit
        return self


class OrderItem(BaseModel):
    """
    The model OrderItem is a cross table that contains the order
    items - one row for each item on an order(so each order can
    generate multiple rows).
    Upon creation it needs to know which :class:`models.Order` and
    :class:`models.Item` are put in relation.

    Attributes:
        order (:any:`Order`): Foreign key pointing to the order that created the `OrderItem`
        item (:any:`Item`): Foreign key pointing to the Item relative to the OrderItem
        quantity (int): Quantity of this Item for the order
        subtotal (:any:`decimal.Decimal`): Calculated subtotal for the OrderItem
    """
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()
    _schema = OrderItemSchema

    def add_item(self, quantity=1):
        """
        Add one item to the OrderItem, increasing the quantity count and
        recalculating the subtotal value for this item(s)
        Args:
            quantity (int): How many items to add
        Returns:
            None
        Raises:
            InsufficientAvailabilityException: If the requested quantity to add
                is higher than the :attr:`models.Item.availability`
        """

        if quantity > self.item.availability:
            raise InsufficientAvailabilityException(self.item, quantity)

        self.item.availability -= quantity
        self.item.save()

        self.quantity += quantity
        self._calculate_subtotal()
        self.save()

    def remove_item(self, quantity=1):
        """
        Remove one item from the OrderItem, decreasing the quantity count and
        recalculating the subtotal value for this item(s)

        Args:
            quantity (int): How many items to add
        Returns:
            int: quantity of items actually removed
        Raises:
            WrongQuantity: If the request for the quantity to remove is higher
                than the quantity present.
        """

        if self.quantity < quantity:
            raise WrongQuantity('Quantity of items to be removed ({}) higher than availability ({})'
                                .format(quantity, self.quantity))

        elif self.quantity > quantity:
            self.quantity -= quantity
            self._calculate_subtotal()
            self.save()
        else:  # elif self.quantity == quantity
            quantity = self.quantity
            self.delete_instance()
        return quantity

    def _calculate_subtotal(self):
        """
        Calculate the subtotal value of the item(s) in the order and update the relative attribute.
        """
        self.subtotal = self.item.price * self.quantity
