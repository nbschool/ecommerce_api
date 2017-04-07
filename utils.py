import os
from flask import abort
from http.client import BAD_REQUEST

IMAGE_FOLDER = 'images'


def check_required_fields(required_fields, request_data):
    """
    Check whether request_data provides all fields in
    required_fields and they are not empty, bad request
    is raised otherwise
    """
    for field in required_fields:
        try:
            value = request_data[field]
            non_empty_str(value, field)
        except (KeyError, ValueError):
            abort(BAD_REQUEST)


def non_empty_str(val, name):
    """ Custom type for reqparser, blocking empty strings. """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


def save_image(file, picture_id, extension):
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
    file.save(image_fullpath(picture_id, extension))


def remove_image(picture_id, extension):
    os.remove(image_fullpath(picture_id, extension))


def image_fullpath(picture_id, extension):
    return os.path.join(
        IMAGE_FOLDER,
        '{}.{}'.format(str(picture_id), extension))
