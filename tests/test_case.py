"""
Test case for setup and teardown methods
"""
# Test utils are the first thing to be imported as they override stuff inside
# standard library such as uuid.uuid4 to generate deterministic values that can
# be reproduced
import tests.test_utils  # noqa:F401

import uuid

from peewee import SqliteDatabase

from app import app
from models import Address, Item, Order, OrderItem, Picture, User

TABLES = [Address, Item, Order, OrderItem, Picture, User]


# @freeze_time('Jan 14th, 2012')
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
        uuid.uuid4.reset()

        for table in TABLES:
            table.delete().execute()
