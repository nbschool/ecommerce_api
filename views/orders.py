from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, INTERNAL_SERVER_ERROR
from models import Order, OrderItem, Item
import sys
sys.path.append('../ecommerce_api')


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
				'item_description': row.orderitem.item.description
			})
		return list(orders.values()), OK
		
	def post(self):	
		res = request.get_json(silent=True)

class OrderHandler(Resource):
	"""Single order endpoints."""
	def get(self, order_id):
		order = {}

		try:
			res = (Order
			.select(Order, OrderItem, Item)
			.join(OrderItem)
			.join(Item)
			.where(Order.order_id == str(order_id)))
	
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
				'item_description': row.orderitem.item.description
				})
			return list(order.values()), OK

		except Order.DoesNotExist:
			return None, NOT_FOUND

	def put(self, order_id):
		pass

	def delete(self, order_id):
		try:
			obj = Order.get(order_id=str(order_id))
			obj2 = OrderItem.get(order=obj)

		except Order.DoesNotExist:
			return None, NOT_FOUND

		obj.delete_instance()
		obj2.delete_instance()
		return None, NO_CONTENT
