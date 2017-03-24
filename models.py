from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import CharField
from peewee import DateTimeField
from peewee import FloatField
from peewee import DecimalField
from peewee import TextField
from peewee import Model
from peewee import SqliteDatabase
from peewee import UUIDField
import uuid
import datetime
import json

DB = 'orders.db'
database = SqliteDatabase(DB)

class BaseModel(Model):
    class Meta:
        database = database

class Item(BaseModel):
    name = CharField(unique=True)
    picture = UUIDField()
    price = DecimalField(decimal_places=2)
    description = TextField()

    def json(self):
        return {
            'name': str(self.name),
            'picture': self.picture,
            'price': self.price,
            'description': self.description
        }

""" The model Order contains a list of orders - one row per order. 
    Each order is placed by a ordeclient. """
class Order(BaseModel):
    order_id = UUIDField(unique=True)
    date = DateTimeField()
    total_price = FloatField()
    delivery_address = CharField()

    class Meta:
        order_by = ('date',)

    def json(self):
        return {
            'order_id': str(self.order_id),
            'date': self.date,
            'total_price': self.total_price,
            'delivery_address': self.delivery_address 
        }

class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = FloatField()

    class Meta:
       indexes = (
           (('order', 'item'), True),
       )
    
    def json(self):
        return {
            'order_id': str(self.order.order_id),
            'item_name': self.item.name,
            'quantity': str(self.quantity),
            'subtotal': self.subtotal
        }

def create_tables():
    database.create_tables([Item, Order, OrderItem], safe=True)

create_tables()

# -------------------------------------------------------------------------

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def populate_tables():
    item1 = Item.create(
        name = "item1",
        picture = uuid.uuid4(),
        price = "20.00",
        description = "item1description."
    )
    item2 = Item.create(
        name = "item2",
        picture = uuid.uuid4(),
        price = "60.00",
        description = "item2description."
    )   
    item3 = Item.create(
        name = "item3",
        picture = uuid.uuid4(),
        price = "100.00",
        description = "item3description."
    )   
    order1 = Order.create(
        order_id = uuid.uuid4(),
        date = json.dumps(datetime.datetime.now(),cls=DateTimeEncoder),
        total_price = 100,
        delivery_address = 'Via Rossi 12'
    )
    orderitem1 = OrderItem.create(
        order = order1,
        item = item1,
        quantity = 2,
        subtotal = 40.00
    )
    orderitem2 = OrderItem.create(
        order = order1,
        item = item2,
        quantity = 1,
        subtotal = 60
    )
    order2 = Order.create(
        order_id = uuid.uuid4(),
        date = json.dumps(datetime.datetime.now(),cls=DateTimeEncoder),
        total_price = 200,
        delivery_address = 'Via Bianchi 10'
    )
    orderitem3 = OrderItem.create(
        order = order2,
        item = item3,
        quantity = 2,
        subtotal = 200
    )

def populate_tables1():
    item1 = Item.create(
        name = "item1",
        picture = uuid.uuid4(),
        price = "20.00",
        description = "item1description."
    )
    order1 = Order.create(
        order_id = uuid.uuid4(),
        date = json.dumps(datetime.datetime.now(),cls=DateTimeEncoder),
        total_price = 100,
        delivery_address = 'Via Rossi 12'
    )
    orderitem1 = OrderItem.create(
        order = order1,
        item = item1,
        quantity = 2,
        subtotal = 50.00
    )

#populate_tables()