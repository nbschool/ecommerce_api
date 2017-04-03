"""
Models contains the database models for the application.
"""
import datetime
from passlib.hash import pbkdf2_sha256
from peewee import DateTimeField, TextField, CharField
from peewee import Model, SqliteDatabase, DecimalField
from peewee import UUIDField

database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        """Automatically update updated_at time during save"""
        self.updated_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = database


class Item(BaseModel):
    """
    Product model
        name: product unique name
        price: product price
        description: product description text
    """
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(auto_round=True)
    description = TextField()

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.item_id,
            self.name,
            self.price,
            self.description)

    def json(self):
        return {
            'item_id': str(self.item_id),
            'name': self.name,
            'price': float(self.price),
            'description': self.description
        }


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

    @staticmethod
    def hash_password(password):
        """Use passlib to get a crypted password.

        :returns: str
        """
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        """
        Verify a clear password against the stored hashed password of the user
        using passlib.

        :returns: bool
        """
        return pbkdf2_sha256.verify(password, self.password)

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
