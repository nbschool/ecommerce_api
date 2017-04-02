import datetime
from flask import Flask, request
from flask_restful import Api, reqparse
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, INTERNAL_SERVER_ERROR
from models import Order, OrderItem, Item, database
import models
import json
import uuid
import sys
sys.path.append('./views')
from orders import OrdersHandler, OrderHandler
import json
import uuid
import datetime

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
		date = datetime.datetime.now().isoformat(),
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
		date = datetime.datetime.now().isoformat(),
		total_price = 200,
		delivery_address = 'Via Bianchi 10'
	)
	orderitem3 = OrderItem.create(
		order = order2,
		item = item3,
		quantity = 2,
		subtotal = 200
	)

populate_tables()
