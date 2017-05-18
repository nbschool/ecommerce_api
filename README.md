[![Build Status](https://api.travis-ci.org/repositories/nbschool/ecommerce_api.svg)](https://travis-ci.org/nbschool/ecommerce_api)

# ecommerce_api
## Getting Started

This document explains our an e-commerce API. The API structure:
* **/views** directory contains the three main elements(item, order and user)
* **/tests** directory contains the test of the main elements
* **models.py** contains the database models for the application
* **app.py** opens and closes the database and carry out the post and put methods of the three elements which can be seen on the server by adding /items/,/orders/ or /users/.
* **schemas.py** checks if the user input data is valid
* **.env** it contains all the environment variables that we use, the content of which is a list of variables = value

## Installing

What you need to install (can be found in the file **requirements.txt**)

## Running the server

To start the server in normal mode:
```
FLASK_APP=app.py flask run
```

To start the server in debug mode:
```
FLASK_DEBUG=1  FLASK_APP=app.py flask run
```

### Heroku
All the env variables should be put in the ```.env``` file, in the root folder. The syntax is, for example:
```
FLASK_APP=app.py
FLASK_DEBUG=1
```

To start the server locally on Heroku:
```
heroku local
```

To use the development Procfile (without gunicorn) use the -f flag:
```
heroku local -f Procfile.dev
```

## Create a TestModel

To create a class that tests some model use:

```
TestCase
```
TestCase is a class that imports all the models and then defines ```setup_class``` and ```setup_method```.
Import your models in **test_case.py**:
```
from models import Item, Order, OrderItem, User
```
add it in ```TABLES``` array:
```
TABLES = [Order, Item, OrderItem, User]
```


Import it in your **test_model.py**:
```
from tests.test_case import TestCase
```
Inherit it in your model:
```
class TestModel(TestCase):
```
Define some function that must starts with ```test```:
```
def test_my_function(self):
    assert True
```

## Running the tests

To perform the test of the project:

```
pytest
```

## Running init_db and demo-content

The init_db is a script that it creates the database with blank tables, or if the database file exists, deleting the database and its tables and create the database with clean tables. There are no parameters and there are no confirmation requests.

To run the script, use the command:
```
PYTHONPATH=. python3 scripts/init_db.py
```

Demo-content is a script which allows the user to generate fake (but realistic) data for all the database tables.

To run the script, use the command:
```
PYTHONPATH=. python3 scripts/demo_content.py
```

There are several * creator * functions that create each record of each table.

## Built With

Python - Used to create the back-end of API


## License

 This project is licensed under [GNU GENERAL PUBLIC LICENSE Version 3](/LICENSE).
