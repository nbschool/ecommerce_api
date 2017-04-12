from auth import auth
from flask import g, request
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK
from models import Address
from utils import check_required_fields

import uuid


class AddressesHandler(Resource):
    """ Addresses endpoint. """
    @auth.login_required
    def get(self):
        user = g.user

        res = (
            Address
            .select()
            .where(Address.user == user)
        )

        return [addr.json() for addr in res], OK

    @auth.login_required
    def post(self):
        user = g.user
        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['country', 'city', 'post_code', 'address', 'phone'])

        addr = Address.create(
            address_id=uuid.uuid4(),
            user=user,
            country=res['country'],
            city=res['city'],
            post_code=res['post_code'],
            address=res['address'],
            phone=res['phone'])

        return addr.json(), CREATED


class AddressHandler(Resource):
    """ Address endpoint. """
    @auth.login_required
    def get(self, address_id):
        user = g.user

        try:
            return Address.get(Address.user == user, Address.address_id == address_id).json(), OK
        except Address.DoesNotExist:
            return None, NOT_FOUND

    @auth.login_required
    def put(self, address_id):
        user = g.user

        try:
            obj = Address.get(Address.user == user, Address.address_id == address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        res = request.get_json()

        check_required_fields(
            request_data=res,
            required_fields=['country', 'city', 'post_code', 'address', 'phone'])

        obj.country = res['country']
        obj.city = res['city']
        obj.post_code = res['post_code']
        obj.address = res['address']
        obj.phone = res['phone']
        obj.save()

        return obj.json(), OK

    @auth.login_required
    def delete(self, address_id):
        user = g.user

        try:
            obj = Address.get(Address.user == user, Address.address_id == address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND
        obj.delete_instance()
        return None, NO_CONTENT
