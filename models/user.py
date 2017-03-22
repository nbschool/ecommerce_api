"""
Models contains the sqlite3 database models for the application.
"""

from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import UUIDField

# TODO: Change database reference when joining all the initial features
database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """
    class Meta:
        database = database


class User(BaseModel):
    """
    User represent an user for the application.

    exposes
    * `get_json()` returns all fields but the password
      as a dictionary ready to be jsonified.
    """

    objectID = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()

    def get_json(self):
        return {
            'id': str(self.objectID),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }
