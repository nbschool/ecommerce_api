from peewee import SqliteDatabase
from colorama import init, Fore, Style
from models import User, Item, Order, OrderItem, Address, Picture, Favorite
import sys


init(autoreset=True)


def drops_all_tables(database):
    """Doesn't drop unknown tables."""
    tables = database.get_tables()
    for table in tables:
        if table == 'item':
            Item.drop_table()
        if table == 'order':
            Order.drop_table()
        if table == 'user':
            User.drop_table()
        if table == 'orderitem':
            OrderItem.drop_table()
        if table == 'address':
            Address.drop_table()
        if table == 'picture':
            Picture.drop_table()
        if table == 'favorite':
            Favorite.drop_table()


def create_tables():
    User.create_table(fail_silently=True)
    Item.create_table(fail_silently=True)
    Order.create_table(fail_silently=True)
    OrderItem.create_table(fail_silently=True)
    Address.create_table(fail_silently=True)
    Picture.create_table(fail_silently=True)
    Favorite.create_table(fail_silently=True)


def good_bye(word, default='has'):
    print(Fore.BLUE + Style.BRIGHT +
          '*-* Your database {1} been {0}. *-*'.format(word, default))
    print(Fore.CYAN + Style.BRIGHT + '*_* Have a nice day! *_*')
    sys.exit()


def create_db():
    db = SqliteDatabase('database.db', autocommit=False)
    if db.is_closed():
        db.connect()
    drops_all_tables(db)
    create_tables()
    good_bye('created')


def main():
    create_db()


if __name__ == '__main__':
    main()
