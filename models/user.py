"""
Models contains the sqlite3 database models for the application.
"""

from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import UUIDField


database = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = database
