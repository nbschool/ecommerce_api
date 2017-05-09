import uuid

import pytest

from tests.test_utils import mock_uuid_generator, MockModelCreate

import models


@pytest.fixture(autouse=True, name='mockuuid4')
def mock_uuid(mocker):
    """
    Override the default uuid.uuid4 function to return a deterministic uuid
    instead of a random one.
    FIXME: When calling a Model.create(), the model stores the original uuid4
    function inside the Field, so this mocking does not work. We could use
    the other fixture to patch the create method, but every Model class has
    different names...
    """
    muuid = mock_uuid_generator()

    def getuuid():
        return next(muuid)
    mockuuid = mocker.patch.object(uuid, 'uuid4', autospec=True)
    mockuuid.side_effect = getuuid


@pytest.fixture(autouse=True, name='mockdatetimes')
def mock_basemodel_datetimes(mocker):
    """
    Patch all the `created_at` and `updated_at` attributes of the peewee models
    defined inside the `models` module.
    """
    with suppress(AttributeError):
        for cls in test_utils.get_all_models_names():
            mocker.patch('models.{}.created_at.default'.format(cls),
                         new=test_utils.mock_datetime)
            mocker.patch('models.{}.updated_at.default'.format(cls),
                         new=test_utils.mock_datetime)
