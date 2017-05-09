"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import SqliteDatabase
from faker import Factory
from colorama import init, Fore, Style
from models import User, Item, Order, OrderItem, Address
import argparse
import sys
import glob
import random


parser = argparse.ArgumentParser()
parser.add_argument('-u','--users', type=int, help='Set up the number of insertions in User table.', default=10, choices=range(10,101))
parser.add_argument('-a','--addresses', type=int, 
                    help='Set up the number of insertions in Address table.', default=10, choices=range(10,101))
parser.add_argument('-i','--items', type=int, 
                    help='Set up the number of insertions in Item table.', default=10, choices=range(10,101))
parser.add_argument('-o','--orders', type=int, 
                    help='Set up the number of insertions in Order table.', default=10, choices=range(10,101))

args = parser.parse_args()
import pdb; pdb.set_trace()

init(autoreset=True)

SEED = 9623954
fake = Factory.create('it_IT')
fake.seed(SEED)
random.seed(SEED)


TEXT_DISPLAY = Fore.MAGENTA + Style.BRIGHT + """
                      WELCOME TO DEMO CONTENT CREATOR.
                      --------------------------------
                    """ + Fore.WHITE + Style.DIM + """
                Here you could create a new simulated database.
                """

MENU_TEXT = Fore.GREEN + Style.BRIGHT + """
                 ***********************************************
                 * Press:                                      *
                 *(1) Overwrite the database                   *
                 *(2) Add data to the current database         *
                 *(Enter) Just to exit                         *
                 ***********************************************
            """

WARNING_DELETE = Fore.YELLOW + Style.BRIGHT + """
                ##################################################
                #   WARNING: YOU WILL DELETE FILES PERMANENTLY   #
                ##################################################
                """

WARNING_OVERWRITE = Fore.YELLOW + Style.BRIGHT + """
                ##################################################
                #   WARNING: YOU WILL CHANGE FILES PERMANENTLY   #
                ##################################################
                """


def get_random_row(table):
    total_rows = table.select().count()
    lucky_row = random.choice(range(1, total_rows+1))
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
        email_user = '{}.{}@{}'.format(first_name.lower(), last_name.lower(), email_provider)
        password = fake.password(length=3, special_chars=False, digits=True,
                                 upper_case=True, lower_case=False)
        User.create(
            user_id=user_uuid,
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
            item_id=item_id,
            name=item_name,
            price=item_price,
            description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
        )


def address_creator(num_addr):
    LIST_COUNTRIES = ['Belgium', 'France', 'Germany',
                      'Greece', 'Italy', 'Portugal', 'Spain']
    for i in range(0, num_addr):
        country = random.choice(LIST_COUNTRIES)
        user_id = count_rows(User)
        Address.create(
            address_id=fake.uuid4(),
            user_id=random.choice(range(1, user_id)),
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
            user_id=random.choice(range(1, user_id)),
            total_price=0,
            delivery_address=random.choice(range(1, address)),
            items=[]
        )


def order_item_creator():
    orders = Order.select()
    for order in orders:
        for e in range(1, random.choice(range(1, 7))):
            an_item = get_random_row(Item)
            quantity = random.choice(range(1, 5))
            order.add_item(an_item, quantity)


def create_db():
    db = SqliteDatabase('database.db', autocommit=True)
    if db.is_closed():
        db.connect()
    set_db(db)
    create_tables()
    write_db()
    good_bye('created')


def write_db():
    """
    Given the SEED 9623954 the first user email is
    'fatima.caputo@tiscali.it', and its password is '9J0.'
    """
    user_creator(10)
    address_creator(10)
    item_creator(10)
    order_creator(10)
    order_item_creator(10)


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
    print(Fore.BLUE + Style.BRIGHT + '*-* Your database {1} been {0}. *-*'.format(word, default))
    print(Fore.CYAN + Style.BRIGHT + '*_* Have a nice day! *_*')
    sys.exit()


def overwrite_db():
    print(WARNING_OVERWRITE, '\n')
    print('Are you sure to overwrite?')
    choice = input('If YES press(1) or [ENTER] to exit without change. >'
                   + Fore.YELLOW + Style.BRIGHT + ' ').strip()
    if choice == '1':
        db = SqliteDatabase('database.db', autocommit=False)
        if db.is_closed():
            db.connect()
        set_db(db)
        drops_all_tables(db)
        create_tables()
        write_db()
        good_bye('overwritten')
    if choice == '':
        good_bye('deleted', default='hasn\'t')


def main():
    starter()
    print(TEXT_DISPLAY)
    list_db = get_databases()
    if len(list_db) == 0:
        print(Fore.GREEN + Style.BRIGHT + 'Do you want a database?')
        choice = input('If YES press(1) or [ENTER] to exit without change. >'
                       + Fore.YELLOW + Style.BRIGHT + ' ').strip()
        if choice == '1':
            create_db()
        if choice == '':
            good_bye('be created', default='hasn\'t')
        else:
            main()
    if len(list_db) != 0:
        print(Fore.YELLOW + Style.BRIGHT + 'You have already a database.')
        print(MENU_TEXT)
        choice = input(Fore.YELLOW + Style.BRIGHT + ' > ').strip()
        if choice == '1':
            overwrite_db()
        if choice == '2':
            write_db(user_num, order_num)
        if choice is '':
            good_bye('change', default='hasn\'t')
        else:
            main()


if __name__ == '__main__':
    main()
