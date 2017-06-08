import json

from models import Item
import search
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


class TestSearchItems(TestCase):
    @classmethod
    def setup_class(cls):
        super(TestSearchItems, cls).setup_class()
        Item.delete().execute()
        for name in NAMES:
            test_utils.add_item(
                name=name,
                description='random description',
                category='',
            )
            pass

        cls.searchEngine = search.SearchEngine(
            ['name', 'description'], limit=10
        )

    def setup_method(self):
        # NOTE: TestCase clear the tables on every method
        # we don't what that, so simple override
        pass

    @classmethod
    def teardown_class(cls):
        Item.delete().execute()

    def search(self, query, attributes=['name', 'description'], limit=10):
        return self.searchEngine(query, Item.select(), attributes, limit)

    def test_search_tavolo_sedie(self):
        result = self.search('tavolo sedie')
        res = ['sedie', 'sedie deco', 'sedie da cucina', 'set di sedie', 'tavolo con sedie',
               'tavolo con set di sedie', 'tavolo', 'tavolo da cucina', 'tavola',
               'tavola di legno']

        assert res == get_names(result)

    def test_search_tavolo(self):
        result = self.search('tavolo')
        res = ['tavolo con sedie', 'tavolo con set di sedie', 'tavolo', 'tavolo da cucina',
               'tavolino', 'tavola', 'tavola di legno', 'legno di tavola']

        assert res == get_names(result)

    def test_search_sedia(self):
        result = self.search('sedia')

        res = ['sedie', 'sedie deco', 'sedie da cucina']
        assert res == get_names(result)

    def test_search_sedie(self):
        result = self.search('sedie')
        res = ['sedie', 'sedie deco', 'sedie da cucina', 'tavolo con sedie',
               'tavolo con set di sedie']

        assert res == get_names(result)

    def test_search_scarpe(self):
        result = self.search('scarpe')
        res = ['scarpe', 'scarpe da ballo', 'scarpe da ginnastica', 'scarpine',
               'scarpette', 'scarpacce']

        assert res == get_names(result)

    def test_search_letto(self):
        result = self.search('letto')

        res = ['divano letto', 'letto', 'letto singolo', 'letto matrimoniale',
               'letto francese']
        assert res == get_names(result)

    def test_search_scarpette(self):
        result = self.search('scarpette')

        res = ['scarpette', 'scarpe']
        assert res == get_names(result)

    def test_search_scarponi(self):
        result = self.search('scarponi')

        res = ['scarponi', 'scarpine']
        assert res == get_names(result)

    def test_search_divano(self):
        result = self.search('divano')

        res = ['divano', 'divano letto']
        assert res == get_names(result)

    def test_search_rest_divano(self):
        resp = self.app.get('/items/db/?query=divano&limit=10')

        assert resp.status_code == 200

        res = ['divano', 'divano letto']
        result = json.loads(resp.data)
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
