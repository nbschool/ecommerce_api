"""
Models contains the database models for the application.
"""
import datetime
from uuid import uuid4

from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField, BooleanField
from peewee import SqliteDatabase, DecimalField
from peewee import UUIDField, ForeignKeyField, IntegerField
from playhouse.signals import Model, post_delete, pre_delete

from exceptions import InsufficientAvailabilityException, WrongQuantity
from schemas import (ItemSchema, UserSchema, OrderSchema, OrderItemSchema,
                     BaseSchema, AddressSchema)
from utils import remove_image


database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    _schema = BaseSchema

    def save(self, *args, **kwargs):
        """Automatically update updated_at time during save"""
        self.updated_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database

    @classmethod
    def get_all(cls):
        return [o for o in cls.select()]

    @classmethod
    def json_list(cls, objs_list):
        return cls._schema.jsonapi_list(objs_list)

    def json(self, include_data=[]):
        parsed, errors = self._schema.jsonapi(self, include_data)
        return parsed

    @classmethod
    def validate_input(cls, data, partial=False):
        return cls._schema.validate_input(data, partial=partial)


class Item(BaseModel):
    """
    Product model
        name: product unique name
        price: product price
        description: product description text
        availability: number of available products of this kind
    """
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()
    availability = IntegerField()
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
    Picture model
        uuid: picture identifier and file name stored
        extension: picture type
        item: referenced item
    """
    uuid = UUIDField(unique=True)
    extension = CharField()
    item = ForeignKeyField(Item, related_name='pictures')

    def filename(self):
        return '{}.{}'.format(
            self.uuid,
            self.extension)

    def json(self):
        return {
            'uuid': str(self.uuid),
            'extension': self.extension,
            'item_uuid': str(self.item.uuid)
        }

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


class User(BaseModel):
    """
    User represents an user for the application.
    Users created are always as role "normal" (admin field = False)
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
        Check that an user exists by checking the email field (unique).
        """
        try:
            User.get(User.email == email)
        except User.DoesNotExist:
            return False
        return True

    @staticmethod
    def hash_password(password):
        """Use passlib to get a crypted password.

        :returns: str
        """
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        """
        Verify a clear password against the stored hashed password of the user
        using passlib.

        :returns: bool
        """
        return pbkdf2_sha256.verify(password, self.password)


class Address(BaseModel):
    """ The model Address represent a user address.
        Each address is releated to one user, but one user can have
        more addresses."""
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name='addresses')
    country = CharField()
    city = CharField()
    post_code = CharField()
    address = CharField()
    phone = CharField()
    _schema = AddressSchema


class Order(BaseModel):
    """ The model Order contains a list of orders - one row per order.
    Each order will be place by one client.
    An order is represented by an uuid,
    a dateTimeField which is the date of the order, a FloatField which
    is the total price of the order. Finally, there is the delivery address,
    if it's different from the customers address from their record.
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
        Returns the list of OrderItem related to the order.
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
        Remove all the items from the order.
        Delete all OrderItem related to this order and reset the total_price
        value to 0.

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

        :param item Item: instance of models.Item
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
        Update the quantity of the orderitem of the given item.
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
        (OrderItem.quantity == 0).
        It also restores the item availability.
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
    """ The model OrderItem is a cross table that contains the order
        items - one row for each item on an order (so each order can
        generate multiple rows).
        It contains two reference field. The first one is a reference
        of the model Order and the other one is for the Item.
        It contains also the quantity of the item and the total price
        of that item.
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

        :returns: int - quantity of items really removed.
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
        """Calculate the subtotal value of the item(s) in the order."""
        self.subtotal = self.item.price * self.quantity
