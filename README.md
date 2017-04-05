# ecommerce_api
Getting Started

 This information serve to explain our an e-commerce API. The API consists of three main elements: item, order and user (saved in the folder views) that communicate with one another and each element has its own testing (saved in the folder tests). There is a file (models.py) in which create the database and contains his models for the application. In the file (app.py) it opens and closes the database and carry out the post and put methods of the three elements which can be seen on the server by adding /items/,/orders/ or /users/. 

Prerequisites
 
 What things you need to install (that can be found in the file requirements.txt):
 
 peewee, httpclientFlask, Flask-RESTful, peewee, pytest, pytest-cov, flask-httpauth, passlib, gunicorn
 
Installing

 How to install them:

 pip3 install <`name of what to install`> for example pip3 install peewee

Running the server

 For running the server using the command:

  FLASK_APP=<`file name`> flask run for example FLASK_APP=app.py flask run

Running the tests

 To perform tests together using the command:
 
  pytest

 To perform a test at a time using the command:

  pytest <`test name`> for example pytest test_items.py

 To perform tests showing for each test if passed or not using the command:

  pytest -v
