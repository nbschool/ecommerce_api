"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import fn
from faker import Factory
from colorama import init, Fore, Style
from models import User, Item, Order, OrderItem, Address, Picture, Favorite
import utils
import argparse
import sys
import glob
import random
import os
import shutil


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


def write_db(num_items, num_users, num_orders, num_addrs, num_pictures, num_favorites):
    """
    Given the SEED 9623954 the first user email is
    'fatima.caputo@tiscali.it', and its password is '9J0.'
    """
    user_creator(num_users)
    address_creator(num_addrs)
    item_creator(num_items)
    order_creator(num_orders)
    order_item_creator(random.randint(1, 7))
    favorite_creator(num_favorites)


def get_databases():
    """create a list with the name of each .db file from main folder."""
    list_of_db = glob.glob('*.db')
    return list_of_db


def get_random_pictures(num_pictures):
    pictures = []
    path = os.path.join('scripts', 'testdata')
    for i in range(0, num_pictures):
        testdata_path = '{}/{}'.format(path, random.choice(os.listdir(path)))
        pictures.append(testdata_path)
    return pictures


def set_db(database):
    Order._meta.database = database
    Item._meta.database = database
    OrderItem._meta.database = database
    User._meta.database = database
    Address._meta.database = database
    Picture._meta.database = database
    Favorite._meta.database = database


def user_creator(num_user):
    """Create users from an Italian-like context. Due to param in factory create 'it_iT'."""
    for i in range(num_user):
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
    LIST_CATEGORIES = ['scarpe', 'accessori', 'abbigliamento uomo', 'abbigliamento donna']
    for i in range(num_item):
        item_id = fake.uuid4()
        item_name = fake.sentence(nb_words=3, variable_nb_words=True)
        item_price = fake.pyfloat(left_digits=2, right_digits=2, positive=True)
        item_category = random.choice(LIST_CATEGORIES)
        item = Item.create(
            uuid=item_id,
            name=item_name,
            price=item_price,
            description=fake.paragraph(
                nb_sentences=3, variable_nb_sentences=True),
            availability=random.randint(35, 60),
            category=item_category,
        )
        picture_creator(num_item, i, item)


def picture_creator(num_picture, index, item):
    ALLOWED_EXTENSION = ['jpg', 'jpeg', 'png', 'gif']
    pictures_path = get_random_pictures(num_picture)
    picture_id = fake.uuid4()
    extension = random.choice(ALLOWED_EXTENSION)
    Picture.create(
        uuid=picture_id,
        extension=extension,
        item=item
    )
    image_folder = utils.get_image_folder()
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    shutil.copy2(pictures_path[index], '/{}/{}.{}'.format(image_folder, picture_id, extension))


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


def favorite_creator(num_favorites):
    for i in range(num_favorites):
        Favorite.create(
            uuid=fake.uuid4(),
            item=Item.select().order_by(fn.Random()).get(),
            user=User.select().order_by(fn.Random()).get(),
            )


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
    parser.add_argument(
        '-p', '--pictures', help='Set up the number of insertions in Picture table.', default=10)

    args = parser.parse_args()
    num_users = args.users
    num_addrs = args.addresses
    num_items = args.items
    num_orders = args.orders
    num_pictures = args.pictures
    num_favorites = 10

    ACTIONS = {
        '1': {
            'key': '1', 'text': 'Add data to the current database',
            'action': lambda: write_db(num_items, num_users, num_orders,
                                       num_addrs, num_pictures, num_favorites)
        },
        '': {
            'key': 'Enter', 'text': 'Just exit',
            'action': lambda: good_bye('change', default='hasn\'t')
        },
    }

    print(TEXT_DISPLAY)
    print(Fore.YELLOW + Style.BRIGHT + 'You have already a database.')
    prompt_menu_1(ACTIONS)


if __name__ == '__main__':
    main()
