"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import SqliteDatabase, fn
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


TEXT_DISPLAY = Fore.MAGENTA + Style.BRIGHT + """
                      WELCOME TO DEMO CONTENT CREATOR.
                      --------------------------------
                    """ + Fore.WHITE + Style.DIM + """
                Here you could create a new simulated database.
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


def set_db(database):
    Order._meta.database = database
    Item._meta.database = database
    OrderItem._meta.database = database
    User._meta.database = database
    Address._meta.database = database


def user_creator(num_user):
    """Create users from an Italian-like context. Due to param in factory create 'it_iT'."""
    for i in range(num_user):
        user_uuid = fake.uuid4()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email_provider = fake.free_email_domain()
        email_user = '{}.{}@{}'.format(first_name.lower(), last_name.lower(), email_provider)
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
    for i in range(num_item):
        item_id = fake.uuid4()
        item_name = fake.sentence(nb_words=3, variable_nb_words=True)
        item_price = fake.pyfloat(left_digits=2, right_digits=2, positive=True)
        Item.create(
            uuid=item_id,
            name=item_name,
            price=item_price,
            description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True),
            availability=random.randint(35, 60),
        )


def address_creator(num_addr):
    LIST_COUNTRIES = ['Belgium', 'France', 'Germany',
                      'Greece', 'Italy', 'Portugal', 'Spain']
    for i in range(num_addr):
        country = random.choice(LIST_COUNTRIES)
        Address.create(
            uuid=fake.uuid4(),
            user=User.select().order_by(fn.Random()).get(),
            country=country,
            city=fake.city(),
            post_code=fake.postcode(),
            address=fake.street_name(),
            phone=fake.phone_number(),
        )


def order_creator(num_order):
    for i in range(num_order):
        order_id = fake.uuid4()
        Order.create(
            uuid=order_id,
            user=User.select().order_by(fn.Random()).get(),
            total_price=0,
            delivery_address=Address.select().order_by(fn.Random()).get(),
            items=[]
        )


def order_item_creator(num_items):
    orders = Order.select()
    for order in orders:
        for e in range(num_items):
            an_item = Item.select().order_by(fn.Random()).get()
            quantity = random.randint(1, 5)
            order.add_item(an_item, quantity)


def create_db(num_items, num_users, num_orders, num_addrs):
    db = SqliteDatabase('database.db', autocommit=True)
    if db.is_closed():
        db.connect()
    set_db(db)
    create_tables()
    write_db(num_items, num_users, num_orders, num_addrs)
    good_bye('created')


def write_db(num_items, num_users, num_orders, num_addrs):
    """
    Given the SEED 9623954 the first user email is
    'fatima.caputo@tiscali.it', and its password is '9J0.'
    """
    user_creator(num_users)
    address_creator(num_addrs)
    item_creator(num_items)
    order_creator(num_orders)
    order_item_creator(random.randint(1, 7))
    import pdb; pdb.set_trace()


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


def overwrite_db(num_items, num_users, num_orders, num_addrs):
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
        write_db(num_items, num_users, num_orders, num_addrs)
        good_bye('overwritten')
    if choice == '':
        good_bye('deleted', default='hasn\'t')


def prompt_menu_1(actions):
    print(Fore.GREEN + Style.BRIGHT + '\t' * 2 + '*' * 47)
    print(Fore.GREEN + Style.BRIGHT + '\t' * 2 + '* Press:' + ' ' * 37 + ' *')
    for action in actions.values():
        print(Fore.GREEN + Style.BRIGHT + '\t' * 2 + '  ({key}) {text}'.format(**action))
    print(Fore.GREEN + Style.BRIGHT + '\t' * 2 + '*' * 47)

    choice = None
    while choice not in actions.keys():
        choice = input(Fore.YELLOW + Style.BRIGHT + ' > ').strip()

    actions[choice]['action']()


def prompt_menu_0(actions):
    print(Fore.GREEN + Style.BRIGHT + 'Do you want a database?')
    choice = None
    while choice not in actions.keys():
        choice = input(Fore.YELLOW + Style.BRIGHT +
                       'If YES press(1) or [ENTER] to exit without change. > ').strip()

    actions[choice]()


def main():
    def check_range(value):
        int_value = abs(int(value))
        if int_value > 100:
            raise argparse.ArgumentTypeError("{} is a big number. Maximum accepted is 100."
                                             .format(int_value))
        return int_value

    parser = argparse.ArgumentParser(description='Set up the number of rows' +
                                     'to insert in each table from CLI.')
    parser.add_argument('-u', '--users', type=check_range, help='Set up the number' +
                        'of insertions in User table.', default=10)
    parser.add_argument('-a', '--addresses', type=check_range,
                        help='Set up the number of insertions in Address table.', default=10)
    parser.add_argument('-i', '--items', type=check_range,
                        help='Set up the number of insertions in Item table.', default=10)
    parser.add_argument('-o', '--orders', type=check_range,
                        help='Set up the number of insertions in Order table.', default=10)

    args = parser.parse_args()
    num_users = args.users
    num_addrs = args.addresses
    num_items = args.items
    num_orders = args.orders

    OVERWRITE_ACTIONS = {
        '1': {
            'key': '1', 'text': 'Overwrite the database',
            'action': lambda: overwrite_db(num_items, num_users, num_orders, num_addrs)
        },
        '2': {
            'key': '2', 'text': 'Add data to the current database',
            'action': lambda: write_db(num_items, num_users, num_orders, num_addrs)
        },
        '': {
            'key': 'Enter', 'text': 'Just exit',
            'action': lambda: good_bye('change', default='hasn\'t')
        },
    }

    NEW_DB_ACTIONS = {
        '1': lambda: create_db(num_items, num_users, num_orders, num_addrs),
        '': lambda: good_bye('be created', default='hasn\'t')
    }

    print(TEXT_DISPLAY)
    list_db = get_databases()
    if len(list_db) == 0:
        prompt_menu_0(NEW_DB_ACTIONS)
    if len(list_db) != 0:
        print(Fore.YELLOW + Style.BRIGHT + 'You have already a database.')
        prompt_menu_1(OVERWRITE_ACTIONS)


if __name__ == '__main__':
    main()
