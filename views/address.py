from flask import request
from flask_login import current_user, login_required
from flask_restful import Resource
from http.client import CREATED, NO_CONTENT, NOT_FOUND, OK, BAD_REQUEST
from models import Address
from utils import generate_response

import uuid


class AddressesHandler(Resource):
    """ Addresses endpoint. """
    @login_required
    def get(self):
        user_addrs = list(Address.select().where(
            Address.user == current_user.id))

        return generate_response(Address.json_list(user_addrs), OK)

    @login_required
    def post(self):
        res = request.get_json(force=True)
        errors = Address.validate_input(res)
        if errors:
            return errors, BAD_REQUEST

        data = res['data']['attributes']

        import pdb; pdb.set_trace()
        addr = Address.create(
            uuid=uuid.uuid4(),
            user=current_user.id,
            country=data['country'],
            city=data['city'],
            post_code=data['post_code'],
            address=data['address'],
            phone=data['phone'])

        return generate_response(addr.json(), CREATED)


class AddressHandler(Resource):
    """ Address endpoint. """
    @login_required
    def get(self, address_uuid):
        try:
            addr = Address.get(
                Address.user == current_user.id,
                Address.uuid == address_uuid
            )
            return generate_response(addr.json(), OK)

        except Address.DoesNotExist:
            return None, NOT_FOUND

    @login_required
    def patch(self, address_uuid):
        try:
            obj = Address.get(Address.user == current_user.id,
                              Address.uuid == address_uuid)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        res = request.get_json(force=True)

        errors = Address.validate_input(res)
        if errors:
            return errors, BAD_REQUEST

        data = res['data']['attributes']

        country = data.get('country')
        city = data.get('city')
        post_code = data.get('post_code')
        address = data.get('address')
        phone = data.get('phone')

        if country and country != obj.country:
            obj.country = country

        if city and city != obj.city:
            obj.city = city

        if post_code and post_code != obj.post_code:
            obj.post_code = post_code

        if address and address != obj.address:
            obj.address = address

        if phone and phone != obj.phone:
            obj.phone = phone

        obj.save()

        return generate_response(obj.json(), OK)

    @login_required
    def delete(self, address_uuid):
        result = Address.delete().where(
            Address.user == current_user.id,
            Address.uuid == address_uuid,
        ).execute()

        if result == 0:
            return None, NOT_FOUND

        return None, NO_CONTENT
