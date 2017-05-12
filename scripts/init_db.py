from peewee import SqliteDatabase
from faker import Factory
from colorama import init, Fore, Style
from models import User, Item, Order, OrderItem, Address
import argparse
import sys
import glob
import random


init(autoreset=True)

SEED = 9623954
fake = Factory.create('it_IT')
fake.seed(SEED)
random.seed(SEED)


def get_random_row(table):
    total_rows = table.select().count()
    lucky_row = random.randint(1, total_rows)
    return table.select().where(table.id == lucky_row).get()


def count_rows(table):
    return table.select().count()


def set_db(database):
    Order._meta.database = database
    Item._meta.database = database
    OrderItem._meta.database = database
    User._meta.database = database
    Address._meta.database = database


def user_creator(num_user):
    """Create users from an Italian-like context. Due to param in factory create 'it_iT'."""
    for i in range(0, num_user):
        user_uuid = fake.uuid4()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email_provider = fake.free_email_domain()
        email_user = '{}.{}@{}'.format(
            first_name.lower(), last_name.lower(), email_provider)
        password = fake.password(length=3, special_chars=False, digits=True,
                                 upper_case=True, lower_case=False)
        User.create(
            uuid=user_uuid,
            first_name=first_name,
            last_name=last_name,
            email=email_user,
            password=User.hash_password(password)
        )


def item_creator(num_item):
    for i in range(0, num_item):
        item_id = fake.uuid4()
        item_name = fake.sentence(nb_words=3, variable_nb_words=True)
        item_price = fake.pyfloat(left_digits=2, right_digits=2, positive=True)
        Item.create(
            uuid=item_id,
            name=item_name,
            price=item_price,
            description=fake.paragraph(
                nb_sentences=3, variable_nb_sentences=True),
            availability=random.randint(35, 60),
        )


def address_creator(num_addr):
    LIST_COUNTRIES = ['Belgium', 'France', 'Germany',
                      'Greece', 'Italy', 'Portugal', 'Spain']
    for i in range(0, num_addr):
        country = random.choice(LIST_COUNTRIES)
        user_id = count_rows(User)
        Address.create(
            uuid=fake.uuid4(),
            user_id=random.randint(1, user_id),
            country=country,
            city=fake.city(),
            post_code=fake.postcode(),
            address=fake.street_name(),
            phone=fake.phone_number(),
        )


def order_creator(num_order):
    for i in range(0, num_order):
        user_id = count_rows(User)
        order_id = fake.uuid4()
        address = count_rows(Address)
        Order.create(
            order_id=order_id,
            user_id=random.randint(1, user_id),
            total_price=0,
            delivery_address=random.randint(1, address),
            items=[]
        )


def order_item_creator(num_items):
    orders = Order.select()
    for order in orders:
        for e in range(1, num_items):
            an_item = get_random_row(Item)
            quantity = random.randint(1, 5)
            order.add_item(an_item, quantity)


def create_db(num_items, num_users, num_orders, num_addrs):
    db = SqliteDatabase('database.db', autocommit=True)
    if db.is_closed():
        db.connect()
    set_db(db)
    create_tables()
    good_bye('created')


def get_databases():
    """create a list with the name of each .db file from main folder."""
    list_of_db = glob.glob('*.db')
    return list_of_db


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


def create_tables():
    User.create_table(fail_silently=True)
    Item.create_table(fail_silently=True)
    Order.create_table(fail_silently=True)
    OrderItem.create_table(fail_silently=True)
    Address.create_table(fail_silently=True)


def good_bye(word, default='has'):
    print(Fore.BLUE + Style.BRIGHT +
          '*-* Your database {1} been {0}. *-*'.format(word, default))
    print(Fore.CYAN + Style.BRIGHT + '*_* Have a nice day! *_*')
    sys.exit()


def overwrite_db(num_items, num_users, num_orders, num_addrs):
    db = SqliteDatabase('database.db', autocommit=False)
    if db.is_closed():
        db.connect()
    set_db(db)
    drops_all_tables(db)
    create_tables()
    good_bye('deleted')


def main():
    parser = argparse.ArgumentParser(
        description='Set up the number of rows' + 'to insert in each table from CLI.')
    parser.add_argument(
        '-u', '--users', help='Set up the number' + 'of insertions in User table.', default=10)
    parser.add_argument(
        '-a', '--addresses', help='Set up the number of insertions in Address table.', default=10)
    parser.add_argument(
        '-i', '--items', help='Set up the number of insertions in Item table.', default=10)
    parser.add_argument(
        '-o', '--orders', help='Set up the number of insertions in Order table.', default=10)

    args = parser.parse_args()
    num_users = args.users
    num_addrs = args.addresses
    num_items = args.items
    num_orders = args.orders

    OVERWRITE_ACTIONS = {overwrite_db(num_items, num_users, num_orders, num_addrs)}


if __name__ == '__main__':
    main()
