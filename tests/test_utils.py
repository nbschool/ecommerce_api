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

from models import Address, User
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
        # import pdb
        # pdb.set_trace()
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


def _test_res_sort_included(result, sortFn=lambda x: x['type']):
    """
    Given a jsonapi response with included data(i.e. an Order that includes
    user, address and items), return the same result with the list of `included`
    sorted using ``sortFn``.

    : param result: jsonapi structure that needs normalization
    : param sortFn: sorting function called on every ``included`` resource.
                   default takes the attribute ``type`` to sort the resources.
    : type sortFn: ``function``
    """
    # safety check.
    if 'included' not in result:
        return result

    def sort(r):
        r['included'] = sorted(r['included'], key=sortFn)
        return r
    if type(result) is list:
        result = [sort(r) for r in result]
    else:
        result = sort(result)

    return result


def _test_res_sort_errors(e):
    """
    Returns the list of errors from a validate_input call, sorted by the
    errors / source / pointer attribute, allowing proper testing.
    """

    e['errors'] = sorted(e['errors'], key=lambda e: e['source']['pointer'])
    return e


def wrong_dump(data):
    """
    Give a wrong encoding (urlencode-like) to the given dictionary
    """
    return reduce(lambda x, y: "{}&{}".format(x, y), [
        "{}={}".format(k, v) for k, v in zip(data.keys(), data.values())])
