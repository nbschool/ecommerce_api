from app import app
from app import Order
from app import Item
from app import OrderItem

from models import database
from models import create_tables
from models import DateTimeEncoder
from models import populate_tables

from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from peewee import SqliteDatabase

import json
import uuid
import datetime

class TestOrders:
	@classmethod
	def setup_class(cls):
		test_db = SqliteDatabase(':memory:')
		Order._meta.database = test_db
		Item._meta.database = test_db
		OrderItem._meta.database = test_db
		test_db.connect()
		Order.create_table(fail_silently=False)
		Item.create_table(fail_silently=False)
		OrderItem.create_table(fail_silently=False)
		cls.app = app.test_client()

	def setup_method(self):
		Order.delete().execute()
		Item.delete().execute()
		OrderItem.delete().execute()

	def test_get_orders__empty(self):
		resp = self.app.get('/orders/')
		assert resp.status_code == OK
		assert json.loads(resp.data) == []

	def test_get_orders(self):
		item1 = Item.create(
			name = "item1",
			picture = uuid.uuid4(),
			price = "20.00",
			description = "item1description."
		)
		oid =  uuid.uuid4()
		dt = json.dumps(datetime.datetime.now(),cls=DateTimeEncoder)
		order1 = Order.create(
			order_id = oid,
			date = dt,
			total_price = 100,
			delivery_address = 'Via Rossi 12'
		)
		orderitem1 = OrderItem.create(
			order = order1,
			item = item1,
			quantity = 2,
			subtotal = 50.00
		)
		resp = self.app.get('/orders/')
		assert resp.status_code == OK
		assert json.loads(resp.data) == [{"order_id": str(oid), "date": dt, "total_price": 100.0, "delivery_address": 'Via Rossi 12', "items": [{"quantity": 2, "subtotal": 50.0, "item_name": "item1", "item_description": "item1description."}]}]

	def test_delete_article__success(self):
		item1 = Item.create(
			name = "item1",
			picture = uuid.uuid4(),
			price = "20.00",
			description = "item1description."
		)
		oid =  uuid.uuid4()
		dt = json.dumps(datetime.datetime.now(), cls=DateTimeEncoder)
		order1 = Order.create(
			order_id = oid,
			date = dt,
			total_price = 100,
			delivery_address = 'Via Rossi 12'
		)
		orderitem1 = OrderItem.create(
			order = order1,
			item = item1,
			quantity = 2,
			subtotal = 50.00
		)
		order2 = Order.create(
			order_id = uuid.uuid4(),
			date = json.dumps(datetime.datetime.now(), cls=DateTimeEncoder),
			total_price = 200,
			delivery_address = 'Via Verdi 12'
		)
		resp = self.app.delete('/orders/{}'.format(str(oid)))
		assert resp.status_code == NO_CONTENT
		assert len(Order.select()) == 1
		assert len(OrderItem.select()) == 0
		assert Order.get(order_id = order2.order_id)

	def test_delete_order__failure_non_existing_empty_articles(self):
		resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
		assert resp.status_code == NOT_FOUND

	def test_delete_order__failure__failure_non_existing(self):
		oid =  uuid.uuid4()
		dt = json.dumps(datetime.datetime.now(),cls=DateTimeEncoder)
		order1 = Order.create(
			order_id = oid,
			date = dt,
			total_price = 100,
			delivery_address = 'Via Rossi 12'
		)
		resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))		
		assert resp.status_code == NOT_FOUND
		assert len(Order.select()) == 1

	def test_db_functionality(self):
		populate_tables()
		# Inner join between the three tables
		res = (Order
			.select()
			.join(OrderItem)
			.join(Item))
		print([o.json() for o in res])
