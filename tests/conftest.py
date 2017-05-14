import uuid

import pytest

from tests.test_utils import mock_uuid_generator, MockModelCreate

import models


@pytest.fixture(autouse=True, name='mockuuid4')
def mock_uuid(mocker):
    """
    Override the default uuid.uuid4 function to return a deterministic uuid
    instead of a random one.
    """
    muuid = mock_uuid_generator()

    def getuuid():
        return next(muuid)
    mockuuid = mocker.patch.object(uuid, 'uuid4', autospec=True)
    mockuuid.side_effect = getuuid


@pytest.fixture(autouse=True, name='mock_create')
def mock_models_create(mocker):
    """
    Patch the create method of our models to force a default created_at datetime
    and a progressive UUID-like UUID object when creating new instances,
    but allowing to override with specific values
    """
    for cls in [models.Order]:
        mocker.patch(
            'models.{}.create'.format(cls.__name__),
            new=MockModelCreate(cls),
        )
