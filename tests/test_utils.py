from functools import reduce
import json
import os
import random
import shutil
from base64 import b64encode
from datetime import timezone
from uuid import uuid4

from models import Address, User
from utils import get_image_folder

random.seed(10485)

def wrong_dump(data):
    """
    Give a wrong encoding (urlencode-like) to the given dictionary
    """
    return reduce(lambda x, y: "{}&{}".format(x, y), [
        "{}={}".format(k, v) for k, v in zip(data.keys(), data.values())])



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
        uuid=id or uuid4(),
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
        uuid=id or uuid4(),
        admin=True,
    )


def add_address(user, country='Italy', city='Pistoia', post_code='51100',
                address='Via Verdi 12', phone='3294882773', id=None):

    return Address.create(
        uuid=id or uuid4(),
        user=user,
        country=country,
        city=city,
        post_code=post_code,
        address=address,
        phone=phone,
    )


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


def format_jsonapi_request(type_, data):
    """
    Given the attributes and relationships of a resource, compile the jsonapi
    post data for the request.
    All key-value pairs except ``relationships`` will be mapped inside
    ``['data']['attributes']`` of the request.
    Relationships key value will be mapped inside ``['data']['relationship']``

    > NOTE:
    > All relationship **must** map to the related field inside the Schema of
    > the type and have a ``type`` and ``id`` properties.

    .. code-block:: python

        data = {
            "<attribute field": "bar"
            "relationships": {
                "<field_name>": {
                    "type": "<Resource type_>",
                    "id": <Resource id>
                },
                "<field_name>": [
                    {
                        "type": "item",
                        "id": <Resource id>
                        "<metadata>": <metadata_value (ie. quantity of items)>
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


def get_expected_results(section):
    """
    Returns the given section of the expected results data from
    `expected_results.json` to validate the response of the flask tests.
    """
    path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(path, 'expected_results.json')
    with open(path) as fo:
        data = json.load(fo)

    return data[section]


def _test_res_patch_id(r, _id):
    """
    When testing a server-created object, patch the result resource id with
    the actual object uuid.
    """
    _id = str(_id)

    def patch_link(link, _id):
        # change the in the link string and return it
        strlist = link.split('/')[:2]
        strlist.append(_id)
        return '/'.join(strlist)

    r['data']['id'] = _id
    r['data']['links']['self'] = patch_link(r['data']['links']['self'], _id)
    r['links']['self'] = patch_link(r['links']['self'], _id)
    return r


def _test_res_patch_date(result, date):
    """
    Patch a jsonapi response date in result['data']['attributes']['date']
    with the given date. If a result list needs to be patched, a matching indexes
    list of dates needs to be given as `date`.

    :param result: a single jsonapi result `dict` or a `list` of result
    :param date: a single `DateTime` object or a **matching** `list` of DateTime
    """
    # patch the attribute
    def patch(r, d):
        r['data']['attributes']['date'] = d

    # add timezone info to match the actual response datetime
    def set_tz(d):
        return d.replace(tzinfo=timezone.utc).isoformat()

    # if result is a list iterate each item.
    # TODO: in this case <date> should be another list with dates with matching
    # indexes
    if type(result) == list:
        for r, d in zip(result, date):
            patch(r, set_tz(d))
    else:
        patch(result, set_tz(date))
    return result
