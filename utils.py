import os
from flask import Response

IMAGE_FOLDER = 'images'


def get_project_root():
    return os.path.dirname(__file__)


def get_image_folder():
    return os.path.join(get_project_root(), IMAGE_FOLDER)


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
        raise ValueError('The argument {} cannot be empty'.format(name))
    return str(val)


def save_image(file, picture_uuid, extension):
    """
    Create an image folder if not exist and then save in the
    folder the image passed with its extension
    """
    if not os.path.exists(get_image_folder()):
        os.makedirs(get_image_folder())
    file.save(image_fullpath(picture_uuid, extension))


def remove_image(picture_uuid, extension):
    """
    Remove a specified picture by picture_uuid from folder
    """
    if os.path.isdir(get_image_folder()) and os.path.isfile(
        image_fullpath(picture_uuid, extension)
    ):
        os.remove(image_fullpath(picture_uuid, extension))
        # TODO log in case file or folder not found


def image_fullpath(picture_uuid, extension):
    """
    Return a path for the image in the image folder,
    with picture_uuid and extension
    """
    return os.path.join(
        get_image_folder(),
        '{}.{}'.format(str(picture_uuid), extension))


def generate_response(data, status, mimetype='application/vnd.api+json'):
    """
    Given a resource model that extends from `BaseModel` generate a Reponse
    object to be returned from the application endpoints'
    """
    return Response(
        response=data,
        status=status,
        mimetype=mimetype
    )


def non_empty_str(val, name):
    """
    Check if a string is empty. If not, raise a ValueError exception.
    """
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)
