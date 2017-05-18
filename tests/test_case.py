"""
Test case for setup and teardown methods
"""

import pytest
from peewee import SqliteDatabase

from app import app
from models import Address, Item, Order, OrderItem, Picture, User, Favorite

TABLES = [Address, Item, Order, OrderItem, Picture, User, Favorite]


@pytest.mark.usefixtures('mockuuid4')
@pytest.mark.usefixtures('mock_create')
class TestCase:
    """
    Created TestCase to avoid duplicated code in the other tests
    """
    TEST_DB = SqliteDatabase(':memory:')

    @classmethod
    def setup_class(cls):
        for table in TABLES:
            table._meta.database = cls.TEST_DB
            table.create_table(fail_silently=True)

        cls.app = app.test_client()

    def setup_method(self):

        for table in TABLES:
            table.delete().execute()
