"""
Models contains the database models for the application.
"""
import datetime

from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField, BooleanField
from peewee import SqliteDatabase, DecimalField
from peewee import UUIDField, ForeignKeyField, IntegerField
from playhouse.signals import Model, post_delete, pre_delete
from uuid import uuid4

from exceptions import InsufficientAvailabilityException
from utils import remove_image


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
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()
    availability = IntegerField()

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.uuid,
            self.name,
            self.price,
            self.description)

    def json(self):
        return {
            'uuid': str(self.uuid),
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'availability': self.availability,
        }


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
            'uuid': str(self.uuid),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }


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

    def json(self):
        return {
            'uuid': str(self.uuid),
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
    An order is represented by an uuid,
    a dateTimeField which is the date of the order, a FloatField which
    is the total price of the order. Finally, there is the delivery address,
    if it's different from the customers address from their record.
    """
    uuid = UUIDField(unique=True, default=uuid4)
    total_price = DecimalField(default=0)
    delivery_address = ForeignKeyField(Address, related_name="orders")
    user = ForeignKeyField(User, related_name="orders")

    class Meta:
        order_by = ('created_at',)

    class OrderItemNotFound(Exception):
        """
        Exception raised when trying to access an OrderItem related to the
        order (i.e. in remove_item(s)) but it cannot be found
        """
        pass

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

    def add_items(self, items):
        """
        Add items to the order from a dict {<Item>: <int:quantity>}. Handles
        creating or updating the OrderItem cross table and the Order total.
        It also updates the item availability counter and raise
        InsufficientAvailability if quantity is less than an item availability.
        :param dict items: {<Item>: <quantity:int>}

        :raises: InsufficientAvailabilityException if a requested quantity is
                 higher than the item availability. If the exception is raised
                 all the changes are reverted.
        """
        orderitems = self.order_items
        with database.atomic():
            for item, quantity in items.items():
                for orderitem in orderitems:
                    # Looping all the OrderItem related to this order,
                    # if one with the same item is found we update that row.
                    if orderitem.item == item:
                        orderitem.add_item(quantity)
                        continue

                if quantity > item.availability:
                    raise InsufficientAvailabilityException(item, quantity)
                # if no matching existing OrderItem is found
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

    def update_items(self, items):
        """
        TODO docstring...
        :param dict items: {<Item>: <difference:int>}
        """
        to_create = {}
        to_remove = {}
        to_patch = {}

        # split items in insert, delete and update sets
        for item, difference in items.items():
            for orderitem in self.order_items:
                if orderitem.item == item:
                    new_quantity = orderitem.quantity + difference
                    if new_quantity == 0:
                        to_remove[item] = difference
                    elif new_quantity > item.availability:
                        raise InsufficientAvailabilityException(
                            item, difference)
                    elif new_quantity < 0:
                        raise Exception
                    else:
                        to_patch[item] = difference
                else:
                    if difference <= 0:
                        raise Exception
                    elif difference > item.availability:
                        raise InsufficientAvailabilityException(
                            item, difference)
                    else:
                        to_create[item] = difference
                self.total_price += (item.price * difference)

        with database.atomic():
            self.patch_items(to_patch)
            self.create_items(to_create)
            self.delete_items(to_remove)
            self.save()

    @database.atomic()
    def patch_items(self, items):
        """
        TODO docstring...
        :param dict items: {<Item>: <difference:int>}
        """
        for item, difference in items.items():
            item.availability += difference
            item.save()
            self.orderitems.get(OrderItem.item == item).update(
                quantity=OrderItem.quantity + difference).execute()

    @database.atomic()
    def delete_items(self, items):
        """
        TODO docstring...
        :param dict items: {<Item>: <quantity:int>}
        """
        for item, quantity in items.items():
            item.availability += quantity
            item.save()

        self.orderitems.delete([
            {
                'order': self.uuid,
                'item': item.uuid,
                'quantity': quantity,
                'subtotal': item.price * quantity
            } for item, quantity in items.items()])

    @database.atomic()
    def create_items(self, items):
        """
        TODO docstring...
        :param dict items: {<Item>: <quantity:int>}
        """
        for item, quantity in items.items():
            item.availability -= quantity
            item.save()

        self.orderitems.insert_many([
            {
                'order': self.uuid,
                'item': item.uuid,
                'quantity': quantity,
                'subtotal': item.price * quantity
            } for item, quantity in items.items()])

    def remove_items(self, items):
        """
        Remove items from an order, handling the relative OrderItem row and
        the Order total price update.
        :param dict items: {<Item>: <quantity:int>}

        :raises: Order.OrderItemNotFound if one of the items does not exists in
                 the order.
                 If the exception is raised all the changes are reverted
        """
        orderitems = self.order_items

        with database.atomic():
            for item, quantity in items.items():
                removed = False
                for orderitem in orderitems:
                    if orderitem.item == item:
                        removed_items = orderitem.remove_item(quantity)
                        self.total_price -= (item.price * removed_items)
                        removed = True
                if not removed:
                    raise Order.OrderItemNotFound(
                        'Item {} is not in the order'.format(item.item_id))

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

    def add_item(self, item, quantity=1):
        """
        Legacy method to add just one item to the order.

        :param Item item: the Item to add
        :param int quantity: how many to add
        """

        return self.add_items({item: quantity})

    def remove_item(self, item, quantity=1):
        """
        Legacy method.
        Remove the given item from the order, reducing quantity of the relative
        OrderItem entity or deleting it if removing the last item
        (OrderItem.quantity == 0).
        It also restores the item availability.
        :param Item item: the Item to remove
        :param int quantity: how many to remove
        """

        for orderitem in self.order_items:
            if orderitem.item == item:
                removed_items = orderitem.remove_item(quantity)
                item.availability += quantity
                item.save()
                self.total_price -= (item.price * removed_items)
                self.save()
                return self

        return self.remove_items({item: quantity})

    def json(self, include_items=False):
        """
        The order json method is different compared to the others, as long as the OrderItem
        cross-table exists.
        With the include_items flag sets to false, the function returns the order json.
        Otherwise, if include_items is equal to true, all the OrderItems and related items
        are included.
        """

        order_json = {
            'uuid': str(self.uuid),
            'date': str(self.created_at),
            'total_price': float(self.total_price),
            'delivery_address': self.delivery_address.json(),
            'user_uuid': str(self.user.uuid)
        }
        if include_items:
            order_json['items'] = self.get_order_items()

        return order_json

    def get_order_items(self):
        """
        Gets all the OrderItems related to an order.
        """

        items = []
        for orderitem in self.order_items:
            items.append({
                'quantity': orderitem.quantity,
                'price': float(orderitem.item.price),
                'subtotal': float(orderitem.subtotal),
                'name': orderitem.item.name,
                'description': orderitem.item.description
            })
        return items


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
            'order_uuid': self.order.uuid,
            'item_uuid': self.item.uuid,
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
