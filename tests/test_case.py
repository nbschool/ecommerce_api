"""
Test case for setup and teardown methods
"""

from app import app
from models import Item, Order, OrderItem, User
from peewee import SqliteDatabase


class TestCase:
    """
    Created TestCase to avoid duplicated code in the other tests
    """
    TEST_DB = SqliteDatabase(':memory:')

    @classmethod
    def setup_class(cls):
        Order._meta.database = cls.TEST_DB
        Item._meta.database = cls.TEST_DB
        OrderItem._meta.database = cls.TEST_DB
        User._meta.database = cls.TEST_DB
        Order.create_table()
        Item.create_table()
        OrderItem.create_table()
        User.create_table()
        cls.app = app.test_client()

    @classmethod
    def teardown_class(cls):
        User.drop_table()
        Item.drop_table()
        Order.drop_table()
        OrderItem.drop_table()

    def setup_method(self):
        Order.delete().execute()
        Item.delete().execute()
        OrderItem.delete().execute()
        User.delete().execute()
