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


def wrong_dump(data):
    """
    Give a wrong encoding (urlencode-like) to the given dictionary
    """
    return reduce(lambda x, y: "{}&{}".format(x, y), [
        "{}={}".format(k, v) for k, v in zip(data.keys(), data.values())])


def add_user(email, psw, id=None):
    """
    Create a single user in the test database.
    If an email is provided it will be used, otherwise it will be generated
    by the function before adding the User to the database.
    """
    email = email or 'johndoe{}@email.com'.format(int(random.random() * 100))

    return User.create(
        first_name='John',
        last_name='Doe',
        email=email,
        password=User.hash_password(psw),
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
    Given the attributes of a resource, compile the jsonapi post data for
    the request.
    """
    return {
        'data': {
            'type': type_,
            'attributes': data
        }
    }


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
    Add the date from a response to an expected result and return it.
    If the result is a list (i.e. get on all orders), set the date for each
    item in the list
    """
    def patch(r, d):
        r['data']['attributes']['date'] = d
    # add timezone info to match the actual response datetime
    date = date.replace(tzinfo=timezone.utc).isoformat()
    if type(result) == list:
        for r in result:
            patch(r, date)
    else:
        patch(result, date)
    return result
