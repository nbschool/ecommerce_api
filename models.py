"""
Models contains the database models for the application.
"""

from passlib.hash import pbkdf2_sha256
from peewee import CharField, Model, SqliteDatabase

database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """
    class Meta:
        database = database


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
        """ Use passlib to get a crypted password. """
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
