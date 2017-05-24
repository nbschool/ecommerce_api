from functools import reduce
import datetime
import inspect
import json
import os
import random
import shutil
import sys
import uuid
from base64 import b64encode

from models import Address, User, Favorite, Item
from utils import get_image_folder


# ###########################################################
# Mocking utilities


def mock_uuid_generator():
    """
    Returns a generator object that creates UUID instances with a deterministic
    and progressive value in the form of `00000000-0000-0000-0000-000000000001`
    """
    i = 1
    while True:
        yield uuid.UUID('00000000-0000-0000-0000-{:012d}'.format(i))
        i += 1


def mock_datetime(*args):
    """
    Datetime mocker fot test suite. Returns fixed time value datetime object.
    """
    return datetime.datetime(2017, 2, 20, 10, 16, 50, 140620)


class MockModelCreate:
    """
    Override callable class that goes in place of the Model.create()
    classmethod and allows extra default custom parameters so test objects can
    be predictable.
    Defaulted attributes are `created_at`, with a static datetime and `uuid`
    with a progressive uuid
    """

    def __init__(self, cls):
        self.original = cls.create
        self.uuid_generator = mock_uuid_generator()

    def __call__(self, created_at=mock_datetime(), uuid=None, **query):
        query['created_at'] = created_at
        query['uuid'] = uuid or next(self.uuid_generator)
        return self.original(**query)


def get_all_models_names():
    """
    Returns the names of all the classes defined inside the 'models' module.
    """
    return [name for
            (name, cls) in inspect.getmembers(
                sys.modules['models'], inspect.isclass)
            if cls.__module__ is 'models']


# ###########################################################
# Peewee models helpers
# Functions to create new instances with overridable defaults


def add_user(email, password, id=None, first_name='John', last_name='Doe'):
    """
    Create a single user in the test database.
    If an email is provided it will be used, otherwise it will be generated
    by the function before adding the User to the database.
    """
    email = email or 'johndoe{}@email.com'.format(int(random.random() * 100))

    return User.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=User.hash_password(password),
        uuid=id or uuid.uuid4(),
    )


def add_admin_user(email, psw, id=None):
    """
    Create a single user in the test database.
    If an email is provided it will be used, otherwise it will be generated
    by the function before adding the User to the database.
    """
    email = email or 'johndoe{}@email.com'.format(int(random.random() * 100))

    return User.create(
        first_name='John Admin',
        last_name='Doe',
        email=email,
        password=User.hash_password(psw),
        uuid=id or uuid.uuid4(),
        admin=True,
    )


def add_address(user, country='Italy', city='Pistoia', post_code='51100',
                address='Via Verdi 12', phone='3294882773', id=None):

    return Address.create(
        uuid=id or uuid.uuid4(),
        user=user,
        country=country,
        city=city,
        post_code=post_code,
        address=address,
        phone=phone,
    )


def add_favorite(self, item, id=None):
    """Link the favorite item to user."""
    return Favorite.create(
            uuid=id or uuid.uuid4(),
            item=item,
            user=self,
    )


def json_favorite(item):
    """Link the favorite item to user."""
    return {
            'item_uuid':item,
    }


def add_item(name='Item Test', price='15.99', description='test test test', id=None):
    return Item.create(
            uuid=id or uuid.uuid4(),
            name=name,
            price=price,
            description=description,
            availability=random.randint(35, 60),
            )


# ###########################################################
# Flask helpers
# Common operations for flask functionalities


def open_with_auth(app, url, method, username, password, content_type, data):
    """Generic call to app for http request. """

    AUTH_TYPE = 'Basic'
    bytes_auth = bytes('{}:{}'.format(username, password), 'ascii')
    auth_str = '{} {}'.format(
        AUTH_TYPE, b64encode(bytes_auth).decode('ascii'))

    return app.open(url,
                    method=method,
                    headers={'Authorization': auth_str},
                    content_type=content_type,
                    data=data)


# ###########################################################
# Images helpers


def clean_images():
    """
    Delete all the images in the IMAGE_FOLDER
    """
    shutil.rmtree(get_image_folder(), onerror=None)


def setup_images():
    """
    Create images folder if doesnt exist
    """
    if not os.path.exists(get_image_folder()):
        os.makedirs(get_image_folder())


# ###########################################################
# JSONAPI testing utilities


path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(path, 'expected_results.json')
with open(path) as fo:
    """
    Expected results dict loaded from `expected_results.json` that can be used
    to match tests operations with flask.
    """
    RESULTS = json.load(fo)


def format_jsonapi_request(type_, data):
    """
    Given the attributes and relationships of a resource, compile the jsonapi
    post data for the request.
    All key - value pairs except ``relationships`` will be mapped inside
    ``['data']['attributes']`` of the request.
    Relationships key value will be mapped inside ``['data']['relationship']``

    > NOTE:
    > All relationship ** must ** map to the related field inside the Schema of
    > the type and have a ``type`` and ``id`` properties.

    .. code-block: : python

        data = {
            "<attribute field": "bar"
            "relationships": {
                "<field_name>": {
                    "type": "<Resource type_>",
                    "id": < Resource id >
                },
                "<field_name>": [
                    {
                        "type": "item",
                        "id": < Resource id > ,
                        "<metadata>": < metadata_value(ie. quantity of items) >
                    }
                ]
            }
        }

    """
    rels = {}
    if 'relationships' in data:
        rels = {k: {'data': v} for k, v in data['relationships'].items()}
        del data['relationships']

    retval = {
        'data': {
            'type': type_,
            'attributes': data,
            'relationships': rels
        }
    }
    return retval


def assert_valid_response(data, expected):
    """
    Take a flask app response.data and the expected test result, normalize them
    sorting the `included` and `errors` lists if present, then assert their
    equality
    """
    def sort_data_lists(data, attribute, key):
        """
        sort a given data structure's attribute (list) using the given key function
        """
        try:
            data[attribute] = sorted(data[attribute], key=key)
        except KeyError:
            pass

    # sort functions for included and errors attributes
    def included_sorter(i): return i['type']

    def errors_sorter(e): return e['source']['pointer']

    try:
        # lazy load of the response data, so we can pass either the parsed json
        # response or the json string
        data = json.loads(data)
    except TypeError:
        # data has already been parsed
        pass

    # ensure that both `data` and `expected` are lists while working on them
    data_items = data if isinstance(data, list) else [data]
    expected_items = expected if isinstance(expected, list) else [expected]

    for item in data_items:
        # Sort the included and errors lists of the response.data if present
        sort_data_lists(item, 'included', included_sorter)
        sort_data_lists(item, 'errors', errors_sorter)

    for item in expected_items:
        # Sort the lists of the expected results if present
        sort_data_lists(item, 'included', included_sorter)
        sort_data_lists(item, 'errors', errors_sorter)

    assert data == expected


def wrong_dump(data):
    """
    Give a wrong encoding (urlencode-like) to the given dictionary
    """
    return reduce(lambda x, y: "{}&{}".format(x, y), [
        "{}={}".format(k, v) for k, v in zip(data.keys(), data.values())])
