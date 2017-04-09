from flask import abort, g, request
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
import uuid
from models import Address, User


class AddressesHandler(Resource):

    @auth.login_required
    def get(self):
        addresses = {}

        res = (
            Address
            .select()
            .where(Address.user == g.user)
        )
        if not res:
            return None, NOT_FOUND

        return res.json(), OK
