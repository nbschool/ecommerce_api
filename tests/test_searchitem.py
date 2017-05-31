

import json

from models import Item
from search import search
from tests import test_utils
from tests.test_case import TestCase

NAMES = [
    'scarpe', 'scarpine', 'scarpette', 'scarpe da ballo',
    'scarpe da ginnastica', 'scarponi', 'scarpacce',
    'sedie', 'sedie deco', 'sedie da cucina', 'set di sedie',
    'tavolo con sedie', 'tavolo con set di sedie', 'divano', 'divano letto',
    'letto', 'letto singolo', 'letto matrimoniale', 'letto francese',
    'poltrona', 'poltrona elettrica', 'sgabello', 'maglietta', 'canottiera',
    'pantaloni', 'mutande', 'tavolo', 'tavolo da cucina', 'tavolino', 'tavola',
    'tavola di legno', 'legno di tavola',
]


def get_names(objects):
    return [r.name for r in objects]


class TestSearchItemsByName(TestCase):
    @classmethod
    def setup_class(cls):
        super(TestSearchItemsByName, cls).setup_class()
        Item.delete().execute()
        for name in NAMES:
            test_utils.add_item(
                name=name,
                description='random description',
                category='',
            )
            pass

    def setup_method(self):
        # NOTE: TestCase clear the tables on every method
        # we don't what that, so simple override
        pass

    @classmethod
    def teardown_class(cls):
        Item.delete().execute()

    def search(self, query, attributes=['name', 'description'], limit=10):
        return search.search(query, attributes, Item, limit)

    def test_search_tavolo_sedie(self):
        result = self.search('tavolo sedie')

        res = ['tavolo con sedie', 'tavolo con set di sedie', 'tavolo da cucina', 'tavolino',
               'tavola di legno', 'sedie', 'set di sedie', 'tavolo', 'tavola', 'scarpe']
        assert res == get_names(result)

    def test_search_tavolo(self):
        result = self.search('tavolo')

        res = ['tavolo', 'tavolino', 'tavola', 'tavola di legno', 'legno di tavola',
               'tavolo con sedie', 'tavolo con set di sedie', 'tavolo da cucina',
               'poltrona', 'letto singolo']
        assert res == get_names(result)

    def test_search_sedia(self):
        result = self.search('sedia')

        res = ['sedie', 'set di sedie', 'sedie da cucina', 'sedie deco', 'divano',
               'tavolo con sedie', 'tavolo con set di sedie', 'divano letto', 'scarpe', 'scarpine']
        assert res == get_names(result)

    def test_search_sedie(self):
        result = self.search('sedie')

        res = ['sedie', 'set di sedie', 'sedie deco', 'sedie da cucina', 'tavolo con sedie',
               'tavolo con set di sedie', 'scarpine', 'scarpe', 'scarpette', 'scarpe da ballo']
        assert res == get_names(result)

    def test_search_scarpe(self):
        result = self.search('scarpe')

        res = ['scarpe', 'scarpine', 'scarpette', 'scarpacce', 'scarponi',
               'scarpe da ballo', 'scarpe da ginnastica', 'sgabello', 'canottiera', 'sedie']
        assert res == get_names(result)

    def test_search_letto(self):
        result = self.search('letto')

        res = ['letto', 'letto matrimoniale', 'divano letto', 'letto singolo', 'letto francese',
               'tavola di legno', 'legno di tavola', 'poltrona elettrica', 'sedie deco', 'tavolo']
        assert res == get_names(result)

    def test_search_scarpette(self):
        result = self.search('scarpette')

        res = ['scarpette', 'scarpe', 'scarpine', 'scarpacce', 'scarponi',
               'scarpe da ginnastica', 'scarpe da ballo', 'maglietta', 'canottiera',
               'letto francese']
        assert res == get_names(result)

    def test_search_scarponi(self):
        result = self.search('scarponi')

        res = ['scarponi', 'scarpine', 'scarpe', 'scarpette', 'scarpacce', 'scarpe da ballo',
               'scarpe da ginnastica', 'sedie', 'sedie deco', 'sedie da cucina']
        assert res == get_names(result)

    def test_search_divano(self):
        result = self.search('divano')

        res = ['divano', 'divano letto', 'scarpe', 'scarpine', 'scarpette',
               'scarpe da ballo', 'scarpe da ginnastica', 'scarponi', 'scarpacce', 'sedie']
        assert res == get_names(result)

    def test_search_rest_divano(self):
        resp = self.app.get('/items/db/?query=divano&limit=10')

        assert resp.status_code == 200
        result = json.loads(resp.data)

        res = ['divano', 'divano letto', 'scarpe', 'scarpine', 'scarpette',
               'scarpe da ballo', 'scarpe da ginnastica', 'scarponi', 'scarpacce', 'sedie']

        assert res == [d['data']['attributes']['name'] for d in result]

    def test_search_rest_no_query_limit_over(self):
        resp = self.app.get('/items/db/?limit=150')

        assert resp.status_code == 400
        data = json.loads(resp.data)

        expected = {
            "errors": [{
                "detail": "Missing query."
            }, {
                "detail": "Limit out of range. must be between 0 and 100. Requested: 150"
            }]
        }

        assert data == expected
