import os
import peewee
from werkzeug import secure_filename

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"

DATABASE = {
    'name': 'ecommerce.db',
    'engine': 'peewee.SqliteDatabase',
}

db = peewee.SqliteDatabase(DATABASE['name'])

PRICE_PRECISION = 2


class BaseModel(peewee.Model):
    """Common features of models"""

    class Meta:
        database = db


class Item(BaseModel):
    """Item model"""
    name = peewee.CharField(unique=True)
    price = peewee.FloatField()
    description = peewee.TextField()

    def __str__(self):
        return u'{}, {}, {}'.format(
            self.name,
            round(float(self.price), PRICE_PRECISION),
            self.description)

    def json(self):
        return {
            'name': self.name,
            'price': round(float(self.price), PRICE_PRECISION),
            'description': self.description
        }


class Picture(BaseModel):
    """Picture model"""
    item = peewee.ForeignKeyField(Item, related_name='pictures')
    image = peewee.CharField()

    @staticmethod
    def save_image(file_obj, item):
        filename = secure_filename(file_obj.filename)
        full_path = os.path.join('images', filename)
        return Picture(item=item, image=full_path)

    def __str__(self):
        return self.image


def connect():
    """
    Establish a connection to the database, create tables
    if not existing already
    """
    if db.is_closed():
        db.connect()
        Item.create_table(fail_silently=True)
        Picture.create_table(fail_silently=True)


def close():
    """Close the database connection"""
    if not db.is_closed():
        db.close()
