import uuid

import pytest
from peewee import DateTimeField

from tests import test_utils
from contextlib import suppress


@pytest.fixture(autouse=True, name='mockuuid4')
def mock_uuid(mocker):
    """
    Override the default uuid.uuid4 function to return a deterministic uuid
    instead of a random one.
    """
    muuid = test_utils.mock_uuid_generator()

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
