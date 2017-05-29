"""
Items view: this module provides methods to interact
with items resources
"""

import http.client as client
import uuid

import jellyfish
from flask import request
from flask_restful import Resource

from models import Item
from utils import generate_response


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

        print('query: {}, limit: {}'.format(query, limit))
        matches = []

        print('Found:')

        for item in Item.select():
            match = jellyfish.jaro_winkler(item.name.lower(), query.lower())

            print('{} -> match: {}'.format(item.name, match))

            if match >= .75:
                matches.append({'item': item, 'match': match})
                print('!!! {}'.format(item.name))

        matches.sort(key=lambda m: m['match'], reverse=True)

        return generate_response(
            Item.json_list([i['item'] for i in matches]),
            client.OK
        )

        # # 1: controllare l'esistenza di questi parametri e la loro validità,
        # # altrimenti BAD_REQUEST
        # if query != '' and (limit > 0 and limit < 100):
        #     return generate_response(query, client.OK)
        # else:
        #     return None, client.BAD_REQUEST
        # # 2: prendere tutti gli item dal database
        # item = Item.get(Item.uuid == item_uuid)
        # # 3: per ogni item calcoliamo la distanza da query usando
        # # distance.hamming

        # #   a: distanza della query dal nome
        # distance.hamming1("query", Item.name, normalized=True)
        # #   b: distanza della query dalla descrizione
        # distance.hamming2("query", Item.description, normalized=True)
        # #   c: facciamo la media delle due distanze
        # average = (distance.hamming1 + distance.hamming2) / 2
        # # 4: ordiniamo la mia lista di item per la distanza da query

        # # 5: ritornimo solo i primi n item come da limit
        # return {}
