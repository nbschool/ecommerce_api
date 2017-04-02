from http.client import CREATED
from http.client import NO_CONTENT
from http.client import OK
from urllib.parse import urljoin
import requests
import json
import uuid 
import datetime

if __name__ == '__main__':
	
	# order = {
	# 	'items': [
	# 		{ 'name': 'item1', 'price': 25000.0, 'quantity': 5 }, 
	# 		{ 'name': 'item2', 'price': 99999.0, 'quantity': 1 },
	# 		{ 'name': 'item3', 'price': 43234.0, 'quantity': 4 }
	# 	],
	# 	'delivery_address': 'Via Rossi 12'
	# }

	# resp = requests.post('http://localhost:5000/orders/', json={'order':  order})
	# # -------------------------------------------------------------------------
	# Test put
	
	order_id =  "ea632e49-a1c1-41dc-9ec0-0e2a8cffe393"
	order = {
		"order_id": order_id,
		'items': [
			{ 'name': 'item1', 'price': 100.0, 'quantity': 5 }, 
			{ 'name': 'item2', 'price': 200.0, 'quantity': 1 }
		],
		'delivery_address': 'Via dfafdsafdafdafds 12'
	}
	resp = requests.put(
				urljoin('http://localhost:5000', 'orders/{}'.format(order_id)), json={'order':  order})
