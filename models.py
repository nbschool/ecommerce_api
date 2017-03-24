import os
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import FloatField
from peewee import TextField
from peewee import ForeignKeyField
from werkzeug import secure_filename

__author__ = "Francesco Mirabelli, Marco Tinacci"
__copyright__ = "Copyright 2017"
__email__ = "ceskomira90@gmail.com, marco.tinacci@gmail.com"

DATABASE = {
    'name': 'ecommerce.db',
    'engine': 'peewee.SqliteDatabase',
}

db = SqliteDatabase(DATABASE['name'])

PRICE_PRECISION = 2


class BaseModel(Model):
    """Common features of models"""

    class Meta:
        database = db


class Item(BaseModel):
    """Item model"""
    name = CharField(unique=True)
    price = FloatField()
    description = TextField()

    def __unicode__(self):
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
    item = ForeignKeyField(Item, related_name='pictures')
    image = CharField()

    def save_image(self, file_obj):
        self.image = secure_filename(file_obj.filename)
        full_path = os.path.join('images', self.image)
        file_obj.save(full_path)
        self.save()

    def __unicode__(self):
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
