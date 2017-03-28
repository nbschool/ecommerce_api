"""
Models contains the database models for the application.
"""
import datetime
from peewee import DateTimeField, TextField, CharField, ForeignKeyField
from peewee import Model, SqliteDatabase, DecimalField

DATABASE = {
    'name': 'database.db',
    'engine': 'peewee.SqliteDatabase',
}

database = SqliteDatabase(DATABASE['name'])


class BaseModel(Model):
    """ Base model for all the database models. """

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        """Automatically update updated_at time during save"""
        self.modified = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database


class Item(BaseModel):
    """Item model"""
    name = CharField(unique=True)
    price = DecimalField(decimal_places=2, auto_round=True)
    description = TextField()

    def __str__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.price,
            self.description)

    def json(self):
        return {
            'name': self.name,
            'price': float(self.price),
            'description': self.description
        }


class Picture(BaseModel):
    """Picture model"""

    image = CharField()

    def json(self):
        return {
            'image': self.image
        }

    def __str__(self):
        return self.image


class ItemPicture(BaseModel):
    """Item-Picture cross-table"""
    item = ForeignKeyField(Item)
    picture = ForeignKeyField(Picture)


class User(BaseModel):
    """
    User represents an user for the application.
    """

    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()

    @staticmethod
    def exists(email):
        """
        Check that an user exists by checking the email field (unique).
        """
        user = User.select().where(User.email == email)

        return user.exists()

    def json(self):
        """
        Returns a dict describing the object, ready to be jsonified.
        """

        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }


# Check if the table exists in the database; if not create it.
# TODO: Use database migration
User.create_table(fail_silently=True)
Item.create_table(fail_silently=True)
Picture.create_table(fail_silently=True)
