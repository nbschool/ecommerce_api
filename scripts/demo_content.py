"""
Drop any test database tables (user, item, order, orderitem)
and supply a new one db with new down-to-earth data.
"""

from peewee import SqliteDatabase
from models import User, Item, Order, OrderItem
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
    User.create(
        user_id="3f369a56-f561-4a3e-b171-43254746f612",
        first_name="Andrea",
        last_name="Santaella",
        email="andrea.santaella@gmail.com",
        password=User.hash_password("AndreaSantaella@1234")
    )

    User.create(
        user_id="ac0935c4-0d31-4473-ab5a-cd873fe2f40a",
        first_name="Benedetta",
        last_name="Forciniti",
        email="benedetta.forciniti@hotmail.com",
        password=User.hash_password("BenedettaForciniti@1234")
    )

    User.create(
        user_id="36492bb5-16ef-495b-b026-fc02d3a82abf",
        first_name="Carlo",
        last_name="Mazzini",
        email="carlo_max@yahoo.it",
        password=User.hash_password("CarloMazzini@1234")
    )

    User.create(
        user_id="d6a8bc83-e0a5-4e32-ad06-13e71c76a64a",
        first_name="Carmela",
        last_name="Esposito",
        email="carmencita@gmail.com",
        password=User.hash_password("CarmelaEsposito2015")
    )

    User.create(
        user_id="92ea81b7-f9ff-4ba4-9891-5aaf863b58cb",
        first_name="Cesare",
        last_name="Secci",
        email="cesarone@virgilio.it",
        password=User.hash_password("salve_cesare34")
    )

    User.create(
        user_id="4e97984c-c5d9-4716-af79-faa9078c1eb7",
        first_name="Cindy",
        last_name="Gelvez",
        email="superstar83@hotmail.it",
        password=User.hash_password("LaCosmica1983")
    )

    User.create(
        user_id="dd225eb3-3aec-49a4-95b0-8076dd6d0335",
        first_name="Daniela",
        last_name="Cortez",
        email="danielita_bella@yahoo.es",
        password=User.hash_password("SupermanVsBatmanNow")
    )

    User.create(
        user_id="8c12cc59-92a1-4e0e-afca-538522053d70",
        first_name="David",
        last_name="Novarin",
        email="dnovarin@yahoo.com",
        password=User.hash_password("125687851")
    )

    User.create(
        user_id="7182f4e7-e6b5-417f-b7be-c04885bbc151",
        first_name="Denimar",
        last_name="Campos",
        email="evergreen27@gmail.com",
        password=User.hash_password("@tYu7jas#12de")
    )

    User.create(
        user_id="f2df0ecf-82fd-496f-9173-9f6ca4c1bb08",
        first_name="Dioclecio",
        last_name="Lombardi",
        email="lombardi_milano@virgilio.it",
        password=User.hash_password("pizzacalda312")
    )

    User.create(
        user_id="e370ff79-8046-4c1e-b11d-bbb8063e3fec",
        first_name="Deucalion",
        last_name="Bruno",
        email="deucalion@gmail.com",
        password=User.hash_password("qPli$sudg2007")
    )

    User.create(
        user_id="e0adb5d7-36e3-4d9c-8405-757ffedba796",
        first_name="Eaco",
        last_name="Montaner",
        email="eaco_montaner@gmail.com",
        password=User.hash_password("FormicaAtomica1989")
    )

    User.create(
        user_id="8462c5bf-31c3-4161-9b55-2b7996e9e662",
        first_name="Ebba",
        last_name="Sanchez",
        email="ebbabebe@yahoo.co.uk",
        password=User.hash_password("LondonILoveYou")
    )

    User.create(
        user_id="2e89dad0-41ce-43f2-91f4-28e53a463193",
        first_name="Zacarías",
        last_name="Mancini",
        email="tiromancino88@virgilio.it",
        password=User.hash_password("#GelatoDiFragola#")
    )

    User.create(
        user_id="178ce777-8d63-476d-bf47-9b12fcdc71c4",
        first_name="Mario",
        last_name="Rossi",
        email="eterno_mario@virgilio.it",
        password=User.hash_password("qwer")
    )

    User.create(
        user_id="4877f031-a661-486f-aca5-4cf05f67b2ee",
        first_name="John",
        last_name="Simpson",
        email="j.simpsom@gmail.com",
        password=User.hash_password("AyCaramba!")
    )

    User.create(
        user_id="859515a2-4d56-4003-a99c-a13ec906e9b1",
        first_name="Brian",
        last_name="Smith",
        email="mrsmith@yahoo.com",
        password=User.hash_password("ThisIsASecret")
    )

    User.create(
        user_id="7343ef59-60e4-47f7-8c6a-90728e53e955",
        first_name="Pedro",
        last_name="Perez",
        email="predito@hotmail.com",
        password=User.hash_password("ElpapaDeLosHelados")
    )

    User.create(
        user_id="b2ec03fd-ab2c-4a88-abed-0f381d0f9e56",
        first_name="Paolo",
        last_name="Giordano",
        email="bucanero2008@yahoo.com",
        password=User.hash_password("###goodkama***")
    )

    User.create(
        user_id="a342521d-8643-4ae1-aedb-59a3a0f44a0c",
        first_name="Naoki",
        last_name="Fukuyama",
        email="isawgozilla@yahoo.co.jp",
        password=User.hash_password("KawaYama")
    )

    User.create(
        user_id="72d02f9f-c3db-49a6-887f-4ee09e2e52d7",
        first_name="Jacopo",
        last_name="Mancini",
        email="foza_viola1972@yahoo.com",
        password=User.hash_password("OhFiorentina!")
    )

    User.create(
        user_id="44ee810a-c925-4fa9-aacd-760ad116f166",
        first_name="Rolan",
        last_name="Adamoli",
        email="inesadamoli@yahoo.co.uk",
        password=User.hash_password("ksdkhgs78¿")
    )

    User.create(
        user_id="91838e23-f95b-41b7-ac49-1951354ecfb1",
        first_name="Livia",
        last_name="Nunez",
        email="livianunez@hotmail.com",
        password=User.hash_password("lisbonaèbona")
    )

    User.create(
        user_id="1e181835-bf05-4557-92d6-6415c3da9a9c",
        first_name="Neve",
        last_name="Turchi",
        email="snow_turchi@hotmail.com",
        password=User.hash_password("biancaneve_dorme")
    )

    User.create(
        user_id="77741629-eb3c-4226-9a0b-94c71617052d",
        first_name="I'timad",
        last_name="Cuevas",
        email="lacaverna2001@gmail.com.com",
        password=User.hash_password("CosmicCromagnon")
    )

    User.create(
        user_id="27efd008-e910-4656-b5aa-0214577f580d",
        first_name="Ziauddin",
        last_name="O'Brian",
        email="bigbrother2017@gmail.com",
        password=User.hash_password("IgnoranceIsPower")
    )

    User.create(
        user_id="01357042-214b-4224-8c6f-2d821fc40b37",
        first_name="Benedita",
        last_name="Chavarria",
        email="beneditach@gmail.com",
        password=User.hash_password("ElChapulinColorado")
    )

    User.create(
        user_id="025a0003-e1be-4866-aa74-81947f44b643",
        first_name="Alejandra",
        last_name="Texeira",
        email="alejandratch@gmail.com",
        password=User.hash_password("allYouNeedIsLove")
    )

    # start create items

    Item.create(
        item_id="ccb909e6-26a5-4693-b8a7-a45a6e53b5db",
        name="Ebony 1Kg Cocoa Mass 96%",
        price=6.82,
        description="Belcolade Ebony cocoa mass the absolute\
                    cocoa experience 96%\ cocoa content."
    )

    Item.create(
        item_id="2440111c-a9ea-4556-827e-f17dc7b416ef",
        name="MO551200-164 25kg CBM183W",
        price=130.25,
        description="Barry Callebaut Milk Chocolate, easimelt."
    )

    Item.create(
        item_id="51c43fd8-0b90-4b96-84da-076da5b23b76",
        name="LCVENE 8x1kg Milk 43% Venezuela Easimelt",
        price=55.44,
        description="Belcolade Milk venezuelan 44.4%.\
                     A strong cocoa taste with an overall\
                     impression of roasted beans. This\
                     combined with a strong accent of nuts,\
                     impregnated with vanilla and caramel,\
                     result in an exclusive milk chocolate."
    )

    Item.create(
        item_id="0424ffca-0352-4aa6-b4eb-0a96f66fe30c",
        name="ZA306/G 15kg milk 41%\ Lait Supreme Easimelt.",
        price=73.05,
        description="Belcolade ZA306/G 15 Kg Milk 41%\ Lait\
                     Supreme Easimelt*\ a dark coloured milk\
                     chocolate with the bitterness of dark\
                     chocolate sweetened with milky notes."
    )

    Item.create(
        item_id="d367821e-3b29-4d82-9ee6-bce88f3f105d",
        name="Wooden kids digital Geometry Clock",
        price=4.50,
        description="Toy in wood with the several characters\
                     from the chocosfera universe."
    )

    Item.create(
        item_id="3e02cba3-5ed6-443f-aa48-b04922834e84",
        name="Java-E4-U70 2.5Kg Milk 32% Java Easymelt",
        price=24.63,
        description="Callebaut Java-T68 2.5% Milk 32% Java Easimelt\
                    java milk chocolate 32% 2.5kg has a typical pale\
                    and reddish colour, typical of the Java cocoa beans\
                    But what a taste sensation! Explicit flaours of sweet\
                    caramel and biscuits and refreshigly fruity, with\
                    slightly acid touches."
    )

    Item.create(
        item_id="1931acbf-bb8c-4684-b91c-d56451e58cf7",
        name="Set mini choco-factory",
        price=148.60,
        description="All your family needs to make real\
                    bean to bar chocolates."
    )

    Item.create(
        item_id="25066cbd-d2c8-4733-a2ae-8b08a1e08498",
        name="Baby Kids Simulator Music Phone Touch Screen.",
        price=12.38,
        description="A beautiful toy with the realistic form\
                    of a smartphone touch screen whit characters\
                    from the Chocosfera."
    )

    Item.create(
        item_id="411c80b0-01db-47e8-a525-1c4c2eaa0fd0",
        name="The golden Coin Maker",
        price=19.99,
        description="Melt, wrap and stamp your own golden foil\
                    covered chocolate coins and medals with Jhon\
                    Adams Golden coin maker. The coin make has a\
                    safe melt chocolate unit for your favoriye brand\
                    of chocolate."
    )

    Item.create(
        item_id="4dc92442-3216-42f0-a613-c82b2599b7af",
        name="PlayGo Chocolate Money Maker",
        price=11.48,
        description="A great activity mini factory set. You can make\
                    hundreds and hundreds of foil wrapped golden\
                    chocolate coins."
    )

    Item.create(
        item_id="3bf0dd02-c485-4ab1-9cc2-65b05827632a",
        name="Chococoin miner",
        price=35.99,
        description="A miner for chococoins base in the\
                    famous raspberry Pi Zero. A beautiful way\
                    to introduce kid in the wonderful world of\
                    criptocurrencies."
    )

    Item.create(
        item_id="773f0a88-fd3b-481b-bb2d-0f05313da781",
        name="Chocosfera Kaoka Plush",
        price=15.99,
        description="A beautiful plush of the Chocosfera's\
                    character Kaoka, godness of the chocolicious\
                    universe."
    )

    Item.create(
        item_id="8232b148-2a76-4b97-9144-1e21de1b4af4",
        name="Chocosfera Pipo Plush",
        price=15.99,
        description="A beautiful plush of the Chocosfera's\
                    character Pipo, The best fiend of men in\
                    the chocolicious universe."
    )

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


# def print_any_db_to_delete(default=1):
#     """In the case there's any db it prints a list in the CLI."""
#     list_of_db = get_databases()
#     lenght_of_list = len(list_of_db)
#     if lenght_of_list > 1:
#         default = lenght_of_list
#         print('You\'ve already {} database in your folder :'.format(default))
#         for index, name_db in enumerate(list_of_db, start=1):
#             print(index, '-', name_db)
#     if lenght_of_list > 1:
#         print('You\'ve already {} databases in your folder :'.format(lenght_of_list))
#         for index, name_db in enumerate(list_of_db, start=1):
#             print(index, '-', name_db)
#     else:
#         pass


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


def create_my_tables():
    User.create_table(fail_silently=True)
    Item.create_table(fail_silently=True)
    Order.create_table(fail_silently=True)
    OrderItem.create_table(fail_silently=True)


def good_bye(word, default='has'):
    print('\033[94m'+'\033[1m'+'*-* Your database {1} been {0}. *-*'.format(word, default))
    print('\033[94m'+'\033[1m'+'*_* Have a nice day! *_*')
    sys.exit()


def remove_unique_db():
    path = []
    get_databases(path)
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
        create_my_tables()
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
            create_my_tables()
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
                    create_my_tables()
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
                create_my_tables()
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
