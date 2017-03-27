from peewee import Model, ForeignKeyField, IntegerField, CharField, DateTimeField, FloatField, DecimalField, TextField, SqliteDatabase, UUIDField
import datetime
import json
import uuid


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
            'name': self.name,
            'picture': self.picture,
            'price': self.price,
            'description': self.description
        }

class Order(BaseModel):
    """ The model Order contains a list of orders - one row per order. 
    Each order is placed by a ordeclient. """
    order_id = UUIDField(unique=True)
    date = DateTimeField()
    total_price = FloatField()
    delivery_address = CharField()

    class Meta:
        order_by = ('date',)

    def json(self):
        return {
            'order_id': self.order_id,
            'date': self.date,
            'total_price': self.total_price,
            'delivery_address': self.delivery_address 
        }

class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = FloatField()
    
    def json(self):
        return {
            'order_id': self.order.order_id,
            'item_name': self.item.name,
            'quantity': str(self.quantity),
            'subtotal': self.subtotal
        }

def create_tables():
    database.create_tables([Item, Order, OrderItem], safe=True)

create_tables()
