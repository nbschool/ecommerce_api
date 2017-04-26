from models import User
from base64 import b64encode
import uuid
import os
import random
import shutil
from utils import IMAGE_FOLDER


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


def clean_images(folder=IMAGE_FOLDER):
    """
    Delete all the images in the IMAGE_FOLDER
    """
    shutil.rmtree(folder, onerror=None)


def setup_images(folder=IMAGE_FOLDER):
    """
    Create images folder if doesnt exist
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
