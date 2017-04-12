"""
Test case for setup and teardown methods
"""

from app import app
from models import Item, Order, OrderItem, User
from peewee import SqliteDatabase

TABLES = [Order, Item, OrderItem, User]


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
