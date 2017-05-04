"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import SqliteDatabase
from models import User, Item, Order, OrderItem, Address
from faker import Factory
from colorama import init, Fore, Style
import os
import sys
import sqlite3
import glob
import random

init(autoreset=True)


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
                 *(2) Add data to the current database          *
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


class CountInsertions:
    def __init__(self, table):
        self.total = table.select().count()

    def random_pick(self):
        pick = random.choice(range(1, self.total+1))
        return pick


class InsertionCall:
    def __init__(self, table):
        self.obj = CountInsertions(table)
        self.lucky_num = self.obj.random_pick()
        self.insert = table.select().where(table.id == self.lucky_num).get()


def set_db(database):
        Order._meta.database = database
        Item._meta.database = database
        OrderItem._meta.database = database
        User._meta.database = database
        Address._meta.database = database


def write_db():
    """
    Given the SEED 9623954 the first user email is
    'fatima.caputo@tiscali.it', and its password is '9J0.'
    """
    SEED = 9623954
    fake = Factory.create('it_IT')
    fake.seed(SEED)
    random.seed(SEED)

    def user_creator(num_user=1):
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

    def item_creator(num_item=1):
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

    def address_creator(num_addr=1):
        LIST_COUNTRIES = ['Belgium', 'France', 'Germany',
                          'Greece', 'Italy', 'Portugal', 'Spain']
        for i in range(0, num_addr):
            country = random.choice(LIST_COUNTRIES)
            user_id = CountInsertions(User)
            Address.create(
                address_id=fake.uuid4(),
                user_id=user_id.random_pick(),
                country=country,
                city=fake.city(),
                post_code=fake.postcode(),
                address=fake.street_name(),
                phone=fake.phone_number(),
            )

    def order_creator(num_order=1):
        for i in range(0, num_order):
            user_id = CountInsertions(User)
            order_id = fake.uuid4()
            address = CountInsertions(Address)
            Order.create(
                order_id=order_id,
                user_id=user_id.random_pick(),
                total_price=0,
                delivery_address=address.random_pick(),
                items=[]
            )

    def order_item_creator(num_order_item=1):
        orders = Order.select()
        for i in orders:
            for e in range(1, random.choice(range(1, 7))):
                an_item = InsertionCall(Item)
                quantity = random.choice(range(1, 5))
                i.add_item(an_item.insert, quantity)

    # start create users

    user_creator(10)

    # start create addresses

    address_creator(10)

    # start create items

    item_creator(10)

    # start create orders

    order_creator(10)

    # start create order_item

    order_item_creator(100)


def get_databases():
    """create a list with the name of each .db file from main folder."""
    list_of_db = glob.glob('*.db')
    return list_of_db


def print_any_db():
    """In the case there's any db it prints a list in the CLI."""
    list_of_db = get_databases()
    lenght_of_list = len(list_of_db)
    word_db = 'database'
    if lenght_of_list > 1:
        word_db = 'databases'
    print(Fore.YELLOW + Style.BRIGHT
          + 'You\'ve already {} {} in your folder :'.format(lenght_of_list, word_db))
    for index, name_db in enumerate(list_of_db, start=1):
        print(index, '-', name_db)
    else:
        good_bye('Error')


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


def remove_unique_db():
    print(WARNING_DELETE)
    print(Fore.RED + Style.BRIGHT + """
          *************************************************************
          *   ARE YOU SURE?!? (You are one step to delete your db).   *
          *************************************************************
          """)
    path = get_databases()
    print('Your database is [{}]'.format(path[0]), end='\n')
    choice_a_db = input(Fore.WHITE + Style.BRIGHT +
                        'Write the name of database to delete\n' +
                        'or hit [ENTER] to exit without changes. >' +
                        Fore.RED + Style.BRIGHT + ' ')
    if choice_a_db == '':
        good_bye('deleted', default='hasn\'t')
    if choice_a_db == path[0]:
        os.remove(path[0])
        good_bye('deleted')
    if choice_a_db != path[0]:
        print(Fore.RED + Style.BRIGHT +
              'ERROR: You typed [{}] instead of [{}]'.format(choice_a_db, path[0]))
        good_bye('deleted', default='hasn\'t')


def remove_chosen_db(lenght_of_list):
    print(WARNING_DELETE)
    list_of_db = get_databases()
    for index, name_db in enumerate(list_of_db, start=1):
        print('( {} ).- {}|'.format(index, name_db), end=' ')
    print('\n')
    choice_a_db = input(Fore.YELLOW + Style.BRIGHT +
                        'Press the number of database to delete ' +
                        'or hit [ENTER] to exit without changes. >' +
                        Fore.RED + Style.BRIGHT + ' ')
    if choice_a_db is '':
        sys.exit()
    else:
        try:
            choice_a_db = int(choice_a_db)-1
        except ValueError:
            print(Fore.RED + Style.BRIGHT + "Oops! That wasn't a number. Try again...")
            sys.exit()
    while True:
        path = list_of_db[choice_a_db]
        if choice_a_db <= lenght_of_list:
            print(Fore.YELLOW + Style.BRIGHT + 'You\'ve chosen {}'.format(path))
            os.remove(path)
            good_bye('deleted')
        else:
            remove_chosen_db()


def overwrite_db():
    print(WARNING_OVERWRITE, '\n')
    print('Are you sure to overwrite?')
    selct = input('if Yes press(1) or [ENTER] to exit without change. >'
                  + Fore.YELLOW + Style.BRIGHT + ' ')


def main():

    print(TEXT_DISPLAY)
    list_db = get_databases()
    if len(list_db) == 0:
        db = SqliteDatabase('database.db', autocommit=True)
        if db.is_closed():
            db.connect()
        print(db.database)
        set_db(db)
        create_tables()
        write_db()
        good_bye('created')
    if len(list_db) != 0:
        print('You have already a database.')
        print(MENU_TEXT)
        choice = input(Fore.YELLOW + Style.BRIGHT + ' > ').strip()
        if choice == '1':
            db = SqliteDatabase('database.db', autocommit=False)
            set_db(db)
            drops_all_tables(db)
            create_tables()
            write_db()
            good_bye('written')
        if choice == '2':
            write_db()
        if choice == '3':
                remove_unique_db()
        if choice is '':
            good_bye('change', default='hasn\'t')
        else:
            main()


if __name__ == '__main__':
    main()
