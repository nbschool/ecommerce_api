import os
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import UUIDField
from peewee import DecimalField
from peewee import TextField
<<<<<<< HEAD
from peewee import ForeignKeyField
from werkzeug import secure_filename

=======
import json
>>>>>>> 2d7167a014e7f42eee306c39696368a15e1b21c5

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

    def json(self):
        return {
            'name': self.name,
            'price': str(self.price),
            'description': self.description
        }

    @staticmethod
    def deserialize(item_json):
        item = json.loads(item_json)
        item['price'] = float(item['price'])
        return item


class Picture(BaseModel):
    item = ForeignKeyField(Item)
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
        db.create_tables([Item], safe=True)


def close():
    if not db.is_closed():
        db.close()
