from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField
from peewee import UUIDField
from peewee import DecimalField
from peewee import TextField

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
    picture = UUIDField()
    price = DecimalField(decimal_places=2)
    description = TextField()

    def json(self):
        return {
            'name': self.name,
            'picture': str(self.picture),
            'price': self.price,
            'description': self.description
        }


def connect():
    if db.is_closed():
        db.connect()
        db.create_tables([Item], safe=True)


def close():
    if not db.is_closed():
        db.close()
