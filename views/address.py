from auth import auth
from flask import abort, g, request
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address

import uuid


class AddressesHandler(Resource):

    @auth.login_required
    def get(self):

        addresses = {}

        res = (
            Address
            .select()
            .where(Address.user == g.user)
        )

        return [addr.json() for addr in res], OK

class AddressHandler(Resource):
    pass
