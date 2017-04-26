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
    """ Custom type for reqparser, blocking empty strings """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


def save_image(file, picture_id, extension, folder=IMAGE_FOLDER):
    """
    Create an image folder if not exist and then save in the
    folder the image passed with its extension
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    file.save(image_fullpath(picture_id, extension))


def remove_image(picture_id, extension, folder=IMAGE_FOLDER):
    """
    Remove a specified picture by picture_id from folder
    """
    if(os.path.isdir(folder)):
        os.remove(image_fullpath(picture_id, extension))
        # TODO log in case folder not found


def image_fullpath(picture_id, extension, folder=IMAGE_FOLDER):
    """
    Return a path for the image with IMAGE_FOLDER
    picture_id and extension
    """
    return os.path.join(folder, '{}.{}'.format(str(picture_id), extension))
