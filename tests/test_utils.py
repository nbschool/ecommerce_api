from functools import reduce
from models import Address, User
from base64 import b64encode
import uuid
import os
import random
import shutil
from utils import get_image_folder


def wrong_dump(data):
    """
    Give a wrong encoding (urlencode-like) to the given dictionary
    """
    return reduce(lambda x, y: "{}&{}".format(x, y), [
        "{}={}".format(k, v) for k, v in zip(data.keys(), data.values())])


def add_user(email, psw):
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
        user_id=uuid.uuid4()
    )


def add_admin_user(email, psw):
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
        user_id=uuid.uuid4(),
        admin=True
    )


def add_address(user, country='Italy', city='Pistoia', post_code='51100',
                address='Via Verdi 12', phone='3294882773'):

    return Address.create(
        address_id=uuid.uuid4(),
        user=user,
        country=country,
        city=city,
        post_code=post_code,
        address=address,
        phone=phone
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
