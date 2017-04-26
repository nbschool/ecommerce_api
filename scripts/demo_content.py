"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import SqliteDatabase
from models import User, Item, Order, OrderItem
from faker import Factory
import os
import sys
import sqlite3
import glob


TEXT_DISPLAY = '\033[95m'+'\033[1m'+"""
                      WELCOME TO DEMO CONTENT CREATOR.
                      --------------------------------
                Here you could create a new simulated database.
                """
MENU_TEXT = '\033[92m'+'\033[1m'+"""
                ***********************************************
                *Press:                                       *
                *(1) To overwrite the database with new data. *
                *(2) Create a new db with a new name.         *
                *(3) delete and exit.                         *
                *(Enter) Just to exit.                        *
                ***********************************************
            """

WARNING_DELETE = '\033[93m'+'\033[1m'+"""
                ##################################################
                #   WARNING: YOU WILL DELETE FILES PERMANENTLY   #
                ##################################################
                """

WARNING_OVERWRITE = '\033[93m'+'\033[1m'+"""
                ##################################################
                #   WARNING: YOU WILL CHANGE FILES PERMANENTLY   #
                ##################################################
                """


def set_db(database):
        Order._meta.database = database
        Item._meta.database = database
        OrderItem._meta.database = database
        User._meta.database = database


def write_db():
    fake = Factory.create('it_IT')
    fake.seed(9623954)

    def user_creator(num_user=1):
        """Create users from an Italian-like context. Due to param in factory create 'it_iT'."""
        num_user = num_user
        for i in range(0, num_user):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email_provider = fake.free_email_domain()
            email_user = '{}.{}@{}'.format(first_name.lower(), last_name.lower(), email_provider)
            password = fake.password(length=3, special_chars=False, digits=True,
                                     upper_case=True, lower_case=False)
            User.create(
                user_id=fake.uuid4(),
                first_name=first_name,
                last_name=last_name,
                email=email_user,
                password=User.hash_password(password)
            )

    def item_creator(num_item=1):
        num_item = num_item
        for i in range(0, num_item):
            Item.create(
                item_id=fake.uuid4(),
                name=fake.sentence(nb_words=3, variable_nb_words=True),
                price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
                description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
            )

    # start create items

    user_creator(10)

    # start create items

    item_creator(100)

    # start create OrderItem entries

    OrderItem.create(
        order_id=1,
        item_id=1,
        quantity=2,
        subtotal=31.98
    )

    # start create order entries

    Order.create(
        order_id="32e0e4e1-39cc-459b-bcdb-50cd73c95f6f",
        total_price=31.98,
        delivery_address="Via dell Albero 56, Firenze. Italia.",
        user_id=1
    )


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
    print('You\'ve already {} {} in your folder :'.format(lenght_of_list, word_db))
    for index, name_db in enumerate(list_of_db, start=1):
        print(index, '-', name_db)
    else:
        good_bye()


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


def create_tables():
    User.create_table(fail_silently=True)
    Item.create_table(fail_silently=True)
    Order.create_table(fail_silently=True)
    OrderItem.create_table(fail_silently=True)


def good_bye(word, default='has'):
    print('\033[94m'+'\033[1m'+'*-* Your database {1} been {0}. *-*'.format(word, default))
    print('\033[94m'+'\033[1m'+'*_* Have a nice day! *_*')
    sys.exit()


def remove_unique_db():
    path = get_databases()
    os.remove('../'+path[0])
    good_bye('deleted')


def remove_chosen_db(list_of):
    list_of_db = get_databases()
    lenght_of_list = len(list_of_db)
    print(WARNING_DELETE)
    for index, name_db in enumerate(list_of_db, start=1):
        print('('+str(index)+')'+'.-', name_db+' |', end=' ')
    print(' ')
    print(' ')
    choice_a_db = input('\033[92m'+'\033[1m'
                        + 'Press the number of database to delete '
                        + 'or hit [ENTER] to exit without changes. > ')
    if choice_a_db is '':
        sys.exit()
    else:
        try:
            choice_a_db = int(choice_a_db)-1
        except ValueError:
            print('\033[91m'+'\033[1m'+"Oops! That wasn't a number. Try again...")
            sys.exit()
    while True:
        path = list_of_db[choice_a_db]
        if choice_a_db <= lenght_of_list:
            print('You\'ve chosen {}'.format(path))
            os.remove(path)
            good_bye('deleted')
        else:
            overwrite_chosen_db(list_of)
            os.remove(path)


def overwrite_unique_db():
    list_of_db = get_databases()
    name_db = list_of_db[0]
    print(WARNING_OVERWRITE, '\n')
    print('You\'ve got only a database')
    print('(1)'+'.-', name_db, end='\n')
    print('Are you sure to overwrite {}?'.format(name_db))
    selct = input('if Yes press(1) or [ENTER] to exit without change. > ')
    if selct is '1':
        db = SqliteDatabase(list_of_db[0], autocommit=False)
        set_db(db)
        drops_all_tables(db)
        create_tables()
        write_db()
        good_bye('written')
    if selct is '':
        good_bye('change', default='hasn\'t')
    else:
        overwrite_unique_db()


def overwrite_chosen_db():
    list_of_db = get_databases()
    lenght_of_list = len(list_of_db)
    print(WARNING_OVERWRITE)
    for index, name_db in enumerate(list_of_db, start=1):
        print('('+str(index)+')'+'.-', name_db+' |', end=' ')
    print(' ')
    print(' ')
    choice_a_db = input('\033[92m'+'\033[1m'
                        + 'Press the number of database to overwrite '
                        + 'or hit [ENTER] to exit without changes. > ')
    if choice_a_db is '':
        sys.exit()
    else:
        try:
            choice_a_db = int(choice_a_db)-1
        except ValueError:
            print('\033[91m'+'\033[1m'+"Oops! That wasn't a number. Try again...")
            sys.exit()
    while True:
        if choice_a_db <= lenght_of_list:
            db = SqliteDatabase(list_of_db[choice_a_db], autocommit=False)
            set_db(db)
            print('You\'ve chosen {}'.format(db.database))
            if db.is_closed():
                db.connect()
            drops_all_tables(db)
            create_tables()
            write_db()
            good_bye('written')
        else:
            overwrite_chosen_db()


def main():

    print(TEXT_DISPLAY)
    while True:
            list_of_db = get_databases()
            lenght_of_list = len(list_of_db)
            print(MENU_TEXT)
            selct = input('Press your choice > ')
            if selct == '1':
                if lenght_of_list == 1:
                    overwrite_unique_db()
                if lenght_of_list == 0:
                    print('No database founded. I\'ll create one for you')
                    db = SqliteDatabase('database.db')
                    set_db(db)
                    create_tables()
                    write_db()
                    good_bye('created')
                else:
                    overwrite_chosen_db()
            if selct == '2':
                name_new_db = input('Write the name of the new db. > ')
                sqlite3.connect(name_new_db+'.db')
                db = SqliteDatabase(name_new_db+'.db', autocommit=True)
                if db.is_closed():
                    db.connect()
                print(db.database)
                set_db(db)
                create_tables()
                write_db()
                good_bye('created')
            if selct == '3':
                print(WARNING_DELETE)
                print_any_db()
                if lenght_of_list == 1:
                    remove_unique_db()
                else:
                    remove_chosen_db(list_of_db)
            if selct == '':
                good_bye('change', 'hasn\'t')


if __name__ == '__main__':
    main()
