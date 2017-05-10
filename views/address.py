from auth import auth
from flask import g, request
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK
from models import Address
from utils import check_required_fields, generate_response

import uuid


class AddressesHandler(Resource):
    """ Addresses endpoint. """
    @auth.login_required
    def get(self):
        user_addrs = list(Address.select().where(Address.user == g.user))

        return generate_response(Address.json_list(user_addrs), OK)

    @auth.login_required
    def post(self):
        res = request.get_json(force=True)

        check_required_fields(
            request_data=res,
            required_fields=['country', 'city', 'post_code', 'address', 'phone'])

        addr = Address.create(
            uuid=uuid.uuid4(),
            user=g.user,
            country=res['country'],
            city=res['city'],
            post_code=res['post_code'],
            address=res['address'],
            phone=res['phone'])

        return generate_response(addr.json(), CREATED)


class AddressHandler(Resource):
    """ Address endpoint. """
    @auth.login_required
    def get(self, address_uuid):
        try:
            addr = Address.get(
                Address.user == g.user,
                Address.uuid == uuid
            )
            return generate_response(addr.json(), OK)

        except Address.DoesNotExist:
            return None, NOT_FOUND

    @auth.login_required
    def patch(self, address_uuid):
        try:
            obj = Address.get(Address.user == g.user,
                              Address.uuid == address_uuid)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        res = request.get_json(force=True)

        country = res.get('country')
        city = res.get('city')
        post_code = res.get('post_code')
        address = res.get('address')
        phone = res.get('phone')

        if country and country != obj.country:
            obj.country = res['country']

        if city and city != obj.city:
            obj.city = res['city']

        if post_code and post_code != obj.post_code:
            obj.post_code = res['post_code']

        if address and address != obj.address:
            obj.address = res['address']

        if phone and phone != obj.phone:
            obj.phone = res['phone']

        obj.save()

        return generate_response(obj.json(), OK)

    @auth.login_required
    def delete(self, address_uuid):
        result = Address.delete().where(
            Address.user == g.user,
            Address.uuid == address_uuid,
        ).execute()

        if result == 0:
            return None, NOT_FOUND

        return None, NO_CONTENT
