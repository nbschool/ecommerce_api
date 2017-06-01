"""
Items view: this module provides methods to interact
with items resources
"""

import http.client as client
import uuid

from flask import request
from flask_restful import Resource
import search

from models import Item
from utils import generate_response


SEARCH_FIELDS = ['name', 'description']


class ItemsHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        data = Item.json_list(Item.select())
        return generate_response(data, client.OK)

    def post(self):
        """
        Insert a new item, the item_uuid identifier is forwarded
        from the one generated from the database
        """
        request_data = request.get_json(force=True)

        errors = Item.validate_input(request_data)
        if errors:
            return errors, client.BAD_REQUEST

        data = request_data['data']['attributes']

        if int(data['availability']) < 0:
            return None, client.BAD_REQUEST

        item = Item.create(
            uuid=uuid.uuid4(),
            name=data['name'],
            price=float(data['price']),
            description=data['description'],
            availability=int(data['availability']),
            category=data['category'],
        )

        return generate_response(item.json(), client.CREATED)


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_uuid):
        """Retrieve the item specified by item_uuid"""
        try:
            item = Item.get(Item.uuid == item_uuid)
            return generate_response(item.json(), client.OK)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

    def patch(self, item_uuid):
        """Edit the item specified by item_uuid"""
        try:
            obj = Item.get(Item.uuid == item_uuid)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json(force=True)

        errors = Item.validate_input(request_data, partial=True)
        if errors:
            return errors, client.BAD_REQUEST

        data = request_data['data']['attributes']

        name = data.get('name')
        price = data.get('price')
        description = data.get('description')
        availability = data.get('availability')
        category = data.get('category')

        if name:
            obj.name = name

        if price:
            obj.price = price

        if description:
            obj.description = description

        if availability:
            obj.availability = availability

        if category:
            obj.category = category

        obj.save()

        return generate_response(obj.json(), client.OK)

    def delete(self, item_uuid):
        """Remove the item specified by item_uuid"""
        try:
            item = Item.get(Item.uuid == item_uuid)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        item.delete_instance()
        return None, client.NO_CONTENT


class SearchItemHandler(Resource):
    def get(self):
        query = request.args.get('query')
        limit = int(request.args.get('limit', -1))
        min_limit, max_limit = 0, 100

        limit_in_range = limit > min_limit and limit <= max_limit

        if query is not None and limit_in_range:
            matches = search.search(query, SEARCH_FIELDS, Item.select(), limit)
            return generate_response(Item.json_list(matches), client.OK)

        def fmt_error(msg):
            return {'detail': msg}

        errors = {"errors": []}
        if not query:
            errors['errors'].append(fmt_error('Missing query.'))
        if not limit_in_range:
            msg = 'Limit out of range. must be between {} and {}. Requested: {}'
            errors['errors'].append(
                fmt_error(msg.format(min_limit, max_limit, limit)))

        return errors, client.BAD_REQUEST
