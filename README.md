# ecommerce_api
## Getting Started

> This document explains our an e-commerce API. The API structure:
* **/views** directory contains the three main elements(item, order and user)
* **/tests** directory contains the test of the main elements
* **models.py** contains the database models for the application
* **app.py** opens and closes the database and carry out the post and put methods of the three elements which can be seen on the server by adding /items/,/orders/ or /users/.
* **schemas.py** checks if the user input data is valid

## Installing
 
 What you need to install (can be found in the file **requirements.txt**)
 
## Running the server

 To start the server in normal mode `FLASK_APP=app.py flask run`

 To start the server in debug mode `FLASK_DEBUG=1  FLASK_APP=app.py flask run`

 To start the server locally on Heroku `heroku local`

## Running the tests

> To perform the test of the project:

   `pytest`

## Built With

 Python - Used to create the back-end of API

## Authors

* **Gianni Valdambrini**
* **Daniele Maccioni**
* **Alessandro Brugioni**
* **German Lugo**
* **Daniele Calcinai**
* **Eugenio Minissale**
* **Francesco Mirabelli**
* **Marco Tinacci**
* **Simone Motta**

## License

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.