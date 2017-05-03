"""
Models contains the database models for the application.
"""
import datetime

from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField, BooleanField
from peewee import Model, SqliteDatabase, DecimalField
from peewee import UUIDField, ForeignKeyField, IntegerField
from uuid import uuid4

from exceptions import InsufficientAvailabilityException


database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        """Automatically update updated_at time during save"""
        self.updated_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database


class Item(BaseModel):
    """
    Product model
        name: product unique name
        price: product price
        description: product description text
        availability: number of available products of this kind
    """
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()
    availability = IntegerField()

    def is_available(self):
        return self.availability > 0

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(
            self.item_id,
            self.name,
            self.price,
            self.description,
            self.availability)

    def json(self):
        return {
            'item_id': str(self.item_id),
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'availability': self.availability,
        }


class User(BaseModel):
    """
    User represents an user for the application.
    Users created are always as role "normal" (admin field = False)
    """
    user_id = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)

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

    def json(self):
        """
        Returns a dict describing the object, ready to be jsonified.
        """

        return {
            'user_id': str(self.user_id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }


class Address(BaseModel):
    """ The model Address represent a user address.
        Each address is releated to one user, but one user can have
        more addresses."""
    address_id = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name='addresses')
    country = CharField()
    city = CharField()
    post_code = CharField()
    address = CharField()
    phone = CharField()

    def json(self):
        return {
            'address_id': str(self.address_id),
            'user_first_name': self.user.first_name,
            'user_last_name': self.user.last_name,
            'country': self.country,
            'city': self.city,
            'post_code': self.post_code,
            'address': self.address,
            'phone': self.phone
        }


class Order(BaseModel):
    """ The model Order contains a list of orders - one row per order.
    Each order will be place by one client.
    An order is represented by an order_id, which is a UUID,
    a dateTimeField which is the date of the order, a FloatField which
    is the total price of the order. Finally, there is the delivery address,
    if it's different from the customers address from their record.
    """
    order_id = UUIDField(unique=True, default=uuid4)
    total_price = DecimalField(default=0)
    delivery_address = ForeignKeyField(Address, related_name="orders")
    user = ForeignKeyField(User, related_name="orders")

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
            .where(Order.order_id == self.order_id)
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
                item.availability -= quantity
                item.save()
                self.total_price += (item.price * quantity)
                self.save()
                return self

        # if no existing OrderItem is found with this order and this Item,
        # create a new row in the OrderItem table
        OrderItem.create(
            order=self,
            item=item,
            quantity=quantity,
            subtotal=item.price * quantity
        )

        self.total_price += (item.price * quantity)
        self.save()
        return self

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

    def json(self):
        return {
            'order_id': str(self.order_id),
            'date': str(self.created_at),
            'total_price': float(self.total_price),
            'delivery_address': self.delivery_address.json(),
            'user_id': str(self.user.user_id)
        }


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

    def json(self):
        return {
            'order_id': self.order.order_id,
            'item_name': self.item.name,
            'quantity': str(self.quantity),
            'subtotal': float(self.subtotal)
        }

    def add_item(self, quantity=1):
        """
        Add one item to the OrderItem, increasing the quantity count and
        recalculating the subtotal value for this item(s)
        """

        if quantity > self.item.availability:
            raise InsufficientAvailabilityException(self.item, quantity)

        self.quantity += quantity
        self._calculate_subtotal()
        self.save()

    def remove_item(self, quantity=1):
        """
        Remove one item from the OrderItem, decreasing the quantity count and
        recalculating the subtotal value for this item(s)

        :returns: int - quantity of items really removed.
        """
        if self.quantity <= quantity:
            # If asked to remove more items than existing, set `quantity` as
            # the total count of items before deleting the row.
            quantity = self.quantity
            self.delete_instance()
        else:
            self.quantity -= quantity
            self._calculate_subtotal()
            self.save()

        return quantity

    def _calculate_subtotal(self):
        """Calculate the subtotal value of the item(s) in the order."""
        self.subtotal = self.item.price * self.quantity


# Check if the table exists in the database; if not create it.
# TODO: Use database migration
User.create_table(fail_silently=True)
Item.create_table(fail_silently=True)
Order.create_table(fail_silently=True)
OrderItem.create_table(fail_silently=True)
Address.create_table(fail_silently=True)
