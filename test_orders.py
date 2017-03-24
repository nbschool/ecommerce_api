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
		da = 'Via Rossi 12'
		order1 = Order.create(
			order_id = oid,
			date = dt,
			total_price = 100,
			delivery_address = da
		)
		orderitem1 = OrderItem.create(
			order = order1,
			item = item1,
			quantity = 2,
			subtotal = 50.00
		)
		resp = self.app.get('/orders/')
		assert resp.status_code == OK
		assert json.loads(resp.data) == [{"order_id": str(oid), "date": dt, "total_price": 100.0, "delivery_address": da, "items": [{"quantity": 2, "subtotal": 50.0, "item_name": "item1", "item_description": "item1description."}]}]

	def test_create_article__success(self):
        source_order = {
	        'items': [
	            {
	                'item_name': 'bla',
	                'quantity': 231,
	                'subtotal': 123.2
	            }
	        ], 
	        'total_price': 32132
    	}
        resp = self.app.post('/orders/', data=source_order)
        assert resp.status_code == CREATED
        order = json.loads(resp.data)

        assert len(ArticleModel.select()) == 1
        assert ArticleModel.get(aid=article['aid']).json() == article
        article.pop('aid')
        assert article == source_article

	def test_db_functionality(self):
		populate_tables()
		# Inner join between the three tables
		res = (Order
			.select()
			.join(OrderItem)
			.join(Item))
		print([o.json() for o in res])
