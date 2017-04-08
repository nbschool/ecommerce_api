"""
Models contains the database models for the application.
"""
import datetime

from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField
from peewee import Model, SqliteDatabase, DecimalField
from peewee import UUIDField, ForeignKeyField, IntegerField
from uuid import uuid4


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
    """
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.item_id,
            self.name,
            self.price,
            self.description)

    def json(self):
        return {
            'item_id': str(self.item_id),
            'name': self.name,
            'price': float(self.price),
            'description': self.description
        }


class User(BaseModel):
    """
    User represents an user for the application.
    """
    user_id = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()

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
            'email': self.email
        }


class Order(BaseModel):
    """ The model Order contains a list of orders - one row per order.
    Each order will be place by one client.
    An order is represented by an order_id, which is a UUID,
    a dateTimeField which is the date of the order, a FloatField which
    is the total price of the order. Finally, there is the delivery address,
    if it's different from the customers address from their record.
    """
    order_id = UUIDField(unique=True)
    date = DateTimeField()
    total_price = DecimalField()
    delivery_address = CharField()

    class Meta:
        order_by = ('date',)

    def __init__(self, *args, **kwargs):

        super(Order, self).__init__(*args, **kwargs)

        self.order_id = uuid4()
        self.date = datetime.datetime.now()
        self.total_price = 0.0

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

    def add_item(self, item):
        """
        Add one item to the order.
        Creates one OrderItem row if the item is not present in the order yet,
        or increasing the count of the existing OrderItem.

        :param item Item: instance of models.Item
        """

        for orderitem in self.order_items:
            # Looping all the OrderItem related to this order, if one with the
            # same item is found we update that row.
            if orderitem.item == item:
                orderitem.add_item()
                return True

        # if no existing OrderItem is found with this order and this Item,
        # create a new row in the OrderItem table
        OrderItem.create(
            order=self,
            item=item,
            quantity=1,
            subtotal=item.price
        )

        self.total_price += item.price
        self.save()
        return True

    def remove_item(self, item):
        """
        Remove the given item from the order, reducing quantity of the relative
        OrderItem entity or deleting it if removing the last item
        (OrderItem.quantity == 0)
        """

        for orderitem in self.order_items:
            if orderitem.item == item:
                orderitem.remove_item()
                self.total_price -= item.price
                self.save()
                return True

        # No OrderItem found for this item
        # TODO: Raise or return something more explicit
        return False

    def json(self):
        return {
            'order_id': str(self.order_id),
            'date': str(self.date),
            'total_price': float(self.total_price),
            'delivery_address': self.delivery_address
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

    def add_item(self):
        """
        Add one item to the OrderItem, increasing the quantity count and
        recalculating the subtotal value for this item(s)
        """
        self.quantity += 1
        self._calculate_subtotal()
        self.save()

    def remove_item(self):
        """
        Remove one item from the OrderItem, decreasing the quantity count and
        recalculating the subtotal value for this item(s)
        """
        if self.quantity <= 1:
            self.delete_instance()
            return True

        self.quantity -= 1
        self._calculate_subtotal()
        self.save()

    def _calculate_subtotal(self):
        """Calculate the subtotal value of the item(s) in the order."""
        self.subtotal = self.item.price * self.quantity


# Check if the table exists in the database; if not create it.
# TODO: Use database migration
User.create_table(fail_silently=True)
Item.create_table(fail_silently=True)
Order.create_table(fail_silently=True)
OrderItem.create_table(fail_silently=True)
