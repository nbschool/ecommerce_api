[![Build Status](https://api.travis-ci.org/repositories/nbschool/ecommerce_api.svg)](https://travis-ci.org/nbschool/ecommerce_api)

# ecommerce_api

## Getting Started


### Installing

    $ pip install -r requirements.txt

### Running the server

To start the server:

    $ FLASK_APP=app.py flask run

Or in debug mode with:

    $ FLASK_DEBUG=1 FLASK_APP=app.py flask run


### Heroku
All the env variables should be put in a `.env` file, in the root folder:

    FLASK_APP=app.py
    FLASK_DEBUG=1

Then run:

    $ heroku local

To run with heroku + gunicorn, or using the development procfile with
    
    $ heroku local -f Procfile.dev


### Running the tests

Run pytest with:

    $ pytest [-v[v]] [-s] [-k <test_name>]


## Running init_db and demo-content

The init_db is a script that creates the database with empty tables, removing them if already present. The script does not accept any parameters and does not ask for user confirmation.

To run the script, use the command:
```
PYTHONPATH=. python3 scripts/init_db.py
```

Demo-content is a script which allows the user to generate fake (but realistic) data for all the database tables.

To run the script, use the command:
```
PYTHONPATH=. python3 scripts/demo_content.py
```

## Building documentation

from the `docs` folder run `make html` to manually build the documentation with sphinx.
For development purposes

    sphinx-autobuild ./source _build_html

can be used to hot reload the documentation that will be served at `127.0.0.1:8000`.

## Built With

Python - Used to create the back-end of API


## License

 This project is licensed under [GNU GENERAL PUBLIC LICENSE Version 3](/LICENSE).
