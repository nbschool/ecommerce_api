from flask import Flask
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import Resource
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import INTERNAL_SERVER_ERROR
import uuid
import datetime
from flask import request
import json

from models import Order, OrderItem, Item, database, populate_tables

app = Flask(__name__)
api = Api(app)

@app.before_request
def _db_connect():
	if database.is_closed():
		database.connect()

@app.teardown_request
def _db_close(exc):
	if not database.is_closed():
		database.close()

def non_emtpy_dict(val, name):
	if not dict(val).strip():
		raise ValueError('The argument {} is not empty'.format(name))
	return str(val)

# Views

class OrdersHandler(Resource):
	"""OrderS endpoint."""
	def get(self):
		orders = {}

		res = (Order
			.select(Order, OrderItem, Item)
			.join(OrderItem)
			.join(Item))

		for row in res:
			if row.order_id not in orders:
				orders[row.order_id] = {
					'order_id': str(row.order_id),
					'date': row.date,
					'total_price': row.total_price,
					'delivery_address': row.delivery_address,
					'items': []
				}
			orders[row.order_id]['items'].append({
				'quantity': row.orderitem.quantity,
				'subtotal': row.orderitem.subtotal,
				'item_name': row.orderitem.item.name,
				'item_description': row.orderitem.item.description,
			})
		return list(orders.values()), OK
		
	def post(self):	
		#res = request.form['order']
		res = request.get_json(silent=True)

		# for i in len(res['order']):
		#  	obj = Order(
		#  		...
		# 	)	
		# 	inserted = obj.save()
		# 	if inserted !=1:
		# 		return None, INTERNAL_SERVER_ERROR
		# return obj.json(), CREATED

class OrderHandler(Resource):
	"""Single order endpoints."""
	def get(self, oid):

		order = {}
		try:
			res = (Order
			.select(Order, OrderItem, Item)
			.join(OrderItem)
			.join(Item)
			.where(Order.order_id == str(oid)))
	
			order = {
				'order_id': str(res[0].order_id),
				'date': res[0].date,
				'total_price': res[0].total_price,
				'delivery_address': res[0].delivery_address,
				'items': []
			}
			for row in res:
				order['items'].append({'quantity': row.orderitem.quantity,
				'subtotal': row.orderitem.subtotal,
				'item_name': row.orderitem.item.name,
				'item_description': row.orderitem.item.description,
				})
			return list(order.values()), OK
		
		except Order.DoesNotExist:
		    return None, NOT_FOUND

    def put(self, oid):
    	try:
    		obj = Order.get(oid=oid)
    	except Order.DoesNotExist:
    		return None, NOT_FOUND

    	res = request.get_json(silent=True)

	def delete(self, oid):
		try:
			obj = Order.get(order_id=str(oid))
			obj2 = OrderItem.get(order=obj)
		except Order.DoesNotExist:
			return None, NOT_FOUND

		obj.delete_instance()
		obj2.delete_instance()
		return None, NO_CONTENT
		
api.add_resource(OrdersHandler, '/orders/')
api.add_resource(OrderHandler, '/orders/<uuid:oid>')

populate_tables()
