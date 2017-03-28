from flask import Flask
from flask_restful import Api, reqparse
from models import database
import sys
sys.path.append('./views')
from orders import OrdersHandler, OrderHandler



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

api.add_resource(OrdersHandler, '/orders/')
api.add_resource(OrderHandler, '/orders/<uuid:order_id>')
