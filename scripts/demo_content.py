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


def get_databases():
    """create a list with the name of each .db file from main folder."""
    list_of_db = glob.glob('*.db')
    return list_of_db


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
        order_id = fake.uuid4()
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
            quantity = random.randint(1, 5)
            order.add_item(an_item, quantity)


def good_bye(word, default='has'):
    print(Fore.BLUE + Style.BRIGHT + '*-* Your database {1} been {0}. *-*'.format(word, default))
    print(Fore.CYAN + Style.BRIGHT + '*_* Have a nice day! *_*')
    sys.exit()


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

    OVERWRITE_ACTIONS = {
        '1': {
            'key': '1', 'text': 'Add data to the current database',
            'action': lambda: write_db(num_items, num_users, num_orders, num_addrs)
        },
        '': {
            'key': 'Enter', 'text': 'Just exit',
            'action': lambda: good_bye('change', default='hasn\'t')
        },
    }

    print(TEXT_DISPLAY)
    list_db = get_databases()
    if len(list_db) != 0:
        print(Fore.YELLOW + Style.BRIGHT + 'You have already a database.')
        prompt_menu_1(OVERWRITE_ACTIONS)


if __name__ == '__main__':
    main()
