"""
Application ORM Models built with Peewee
"""
import datetime
import os
from exceptions import InsufficientAvailabilityException, WrongQuantity
from uuid import uuid4

from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
from peewee import (BooleanField, CharField, DateTimeField, DecimalField,
                    ForeignKeyField, IntegerField, PostgresqlDatabase,
                    TextField, UUIDField)
from playhouse.signals import Model, post_delete, pre_delete

from schemas import (AddressSchema, BaseSchema, FavoriteSchema, ItemSchema,
                     OrderItemSchema, OrderSchema, PictureSchema, UserSchema)
import search
from utils import remove_image


ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
if ENVIRONMENT != 'dev':
    import urllib.parse
    urllib.parse.uses_netloc.append('postgres')
    url = urllib.parse.urlparse(os.getenv('DATABASE_URL'))
    database = PostgresqlDatabase(database=url.path[1:],
                                  user=url.username,
                                  password=url.password,
                                  host=url.hostname,
                                  port=url.port,
                                  )

else:
    from peewee import SqliteDatabase
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

    #: Each model that needs to implement the search functionality `should`
    #: override this attribute with the fields that needs to be checked while
    #: searching.
    #: Attribute should be a list of names of class attributes (strings)
    _search_attributes = None
    #: Attributes weights can be specified with a list of numbers that will
    #: map each weight to attributes (:any:`BaseModel._search_attributes`)
    #: indexes.
    _search_weights = None

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

    @classmethod
    def search(cls, query, dataset, limit=-1,
               attributes=None, weights=None,
               threshold=search.config.THRESHOLD):
        """
        Search a list of resources with the callee class.

        Arguments:
            query (str): Query to lookup for
            dataset (iterable): sequence of resource objects to lookup into
            limit (int): maximum number of resources to return (default -1, all)
            attributes (list): model attribute names. Can be set as default
                inside the model definition or specified on the fly while
                searching.
            weights (list): attributes weights values,indexes should
                match the attribute position in the `attributes` argument.
                if length does not match it will be ignored.
            threshold (float): value between 0 and 1, identify the matching
                threshold for a result to be included.

        Returns:
            list: list of resources that may match the query.

        Raises:
            AttributeError:
                if ``attributes`` are missing, either as model
                default in ``<Model>._search_attributes`` or as param
                one of the object does not have one of the given attribute(s).

        Examples:

            .. code-block:: python

                results = Item.search('shoes', Item.select(), limit=20)
        """

        attributes = attributes or cls._search_attributes
        weights = weights or cls._search_weights

        if not attributes:
            raise ValueError(
                'Attributes to look for not defined for {}. \
                Please update the Model or specify during search call.\
                '.format(cls.__name__))

        return search.search(query, attributes, dataset, limit, threshold, weights)


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
    _search_attributes = ['name', 'category', 'description']

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.uuid,
            self.name,
            self.price,
            self.description)

    def is_favorite(self, item):
        for f in self.favorites:
            if f.item_id == item.id:
                return True
        return False


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

    def add_favorite(user, item):
        """Link the favorite item to user."""
        return Favorite.create(
            uuid=uuid4(),
            item=item,
            user=user,
        )

    def delete_favorite(self, obj):
        obj.delete_instance()


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
            models.Order: The updated order
        """

        self.total_price = 0
        OrderItem.delete().where(OrderItem.order == self).execute()
        self.save()
        return self

    @staticmethod
    def create_order(user, address, items):
        """
        Create an Order and respective OrderItems. OrderItems are created
        in a single query as well as the Order. It also updates Items'
        availability.

        Args:
            user (models.User): order owner
            address (models.Address): order address
            items (dict): item updates entries as a dictionary, keys are
                items and values are new quantities to set. Example of
                argument:

                ..code-block:: python
                    items = {
                        Item.get(pk=1): 3,
                        Item.get(pk=2): 1,
                    }

        Returns:
            models.Order: The new order
        """
        total_price = sum(
            item.price * quantity for item, quantity in items.items())

        with database.atomic():
            order = Order.create(
                delivery_address=address,
                user=user,
                total_price=total_price,
            )
            order.update_items(items, update_total=False)
            return order

    def update_items(self, items, update_total=True, new_address=None):
        """
        Update Order and respective OrderItems by splitting in creation,
        deletion and updating queries, minimizing the interactions with the
        database. It also updates Items' availability.

        Args:
            items (dict): item updates entries as a dictionary, keys are
                items and values are new quantities to set. Example of
                argument:

                ..code-block:: python
                    items = {
                        Item.get(pk=1): 3,
                        Item.get(pk=2): 0,
                        Item.get(pk=3): 1,
                    }
            update_total (bool): if True the procedure updates order's
                total price. Default to True.
            new_address (models.Address): if not None the procedure updates
                the order with the given address. Default to None.

        Returns:
            models.Order: The new/updated order
        """
        to_create = {}
        to_remove = {}
        to_edit = {}
        total_price_difference = 0
        orderitems = self.order_items

        # split items in insert, delete and update sets
        for item, quantity in items.items():
            for orderitem in orderitems:
                if orderitem.item == item:
                    difference = quantity - orderitem.quantity
                    if quantity == 0:
                        to_remove[item] = orderitem.quantity
                    elif difference > item.availability:
                        raise InsufficientAvailabilityException(
                            item, quantity)
                    elif quantity < 0:
                        raise WrongQuantity()
                    else:
                        to_edit[item] = difference
                    total_price_difference += item.price * difference
                    break
            else:
                if quantity <= 0:
                    raise WrongQuantity()
                elif quantity > item.availability:
                    raise InsufficientAvailabilityException(
                        item, quantity)
                else:
                    to_create[item] = quantity
                total_price_difference += item.price * quantity

        with database.atomic():
            self.edit_items_quantity(to_edit)
            self.create_items(to_create)
            self.delete_items(to_remove)
            if update_total:
                self.total_price += total_price_difference
            if new_address:
                self.address = new_address
            if update_total or new_address:
                self.save()
        return self

    @database.atomic()
    def edit_items_quantity(self, items):
        """
        Update orderitems using a query for each item, and updates
        items' availability.

        Args:
            items (dict): item updates entries as a dictionary, keys are
                items and values are new quantities to set. Example of
                argument:

                ..code-block:: python
                    items = {
                        Item.get(pk=1): 3,
                        Item.get(pk=3): 1,
                    }
        Returns:
            Order: callee instance
        """
        if not items:
            return

        orderitems = OrderItem.select().where(
            OrderItem.item << [k for k in items.keys()],
            OrderItem.order == self)

        for orderitem in orderitems:
            for item, difference in items.items():
                if orderitem.item == item:
                    item.availability -= difference
                    item.save()
                    orderitem.quantity += difference
                    orderitem._calculate_subtotal()
                    orderitem.save()
                    break

    def delete_items(self, items):
        """
        Delete orderitems in a single query and updates items' availability.

        Args:
            items (dict): item entries as a dictionary, keys are
                items to delete and values are previously reserved quantities.
                Example of argument:

                ..code-block:: python
                    items = {
                        Item.get(pk=1): 3,
                        Item.get(pk=2): 2,
                    }
        """
        if not items:
            return

        with database.atomic():
            for item, quantity in items.items():
                item.availability += quantity
                item.save()
            OrderItem.delete().where(
                OrderItem.order == self).where(
                OrderItem.item << [k for k in items.keys()]).execute()

    def create_items(self, items):
        """
        Creates orderitems in a single query and updates items' availability.

        Args:
            items (dict): item entries as a dictionary, keys are
                items to create and values are new quantities to set.
                Example of argument:

                ..code-block:: python
                    items = {
                        Item.get(pk=1): 3,
                        Item.get(pk=2): 1,
                    }
        """
        if not items:
            return

        with database.atomic():
            for item, quantity in items.items():
                item.availability -= quantity
                item.save()

            OrderItem.insert_many([
                {
                    'order': self,
                    'item': item,
                    'quantity': quantity,
                    'subtotal': item.price * quantity,
                } for item, quantity in items.items()]).execute()

    def add_item(self, item, quantity=1):
        """
        Add items to the order. It updates item availability.

        Args:
            item (models.Item): the Item to add
            quantity (int): how many items to add

        Returns:
            order (models.Order): the updated order
        """
        return self.update_items({item: quantity})

    def remove_item(self, item, quantity=1):
        """
        Remove the given item from the order, reducing quantity of the relative
        OrderItem entity or deleting it if removing the last item
        ``(OrderItem.quantity == 0)``.
        It also restores the item availability.

        Args:
            item (models.Item): the Item to remove
            quantity (int): how many items to remove

        Returns:
            order (models.Order): the updated order
        """
        return self.update_items({item: -quantity})


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


class Favorite(BaseModel):
    """ Many to many table to relate an item with a user."""
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name="favorites")
    item = ForeignKeyField(Item, related_name="favorites")
    _schema = FavoriteSchema
