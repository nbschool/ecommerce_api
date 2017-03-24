import os
import json
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import DecimalField
from peewee import TextField
from peewee import ForeignKeyField
from werkzeug import secure_filename

DATABASE = {
    'name': 'ecommerce.db',
    'engine': 'peewee.SqliteDatabase',
}

db = SqliteDatabase(DATABASE['name'])


class BaseModel(Model):
    def get_content(self):
        return self._data

    class Meta:
        database = db


class Item(BaseModel):
    name = CharField(unique=True)
    price = DecimalField(decimal_places=2)
    description = TextField()

    def __unicode__(self):
        return u'{}, {}, {}'.format(
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
    if db.is_closed():
        db.connect()
        db.create_tables([Item, Picture], safe=True)


def close():
    if not db.is_closed():
        db.close()
