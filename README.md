# ecommerce_api
## Getting Started

> This information serve to explain our an e-commerce API. The API structure:
* **/views** directory contains the three main elements(item, order and user)
* **/tests** directory contains the test of the main elements
* **models.py** contains the database models for the application
* **app.py** opens and closes the database and carry out the post and put methods of the three elements which can be seen on the server by adding /items/,/orders/ or /users/.
* **schemas.py** checks if the user input data is valid

## Prerequisites
 
 What things you need to install (can be found in the file **requirements.txt**)
 
## Running the server

 Run the server in normal mode **FLASK_APP=app.py flask run**

 Run the server in debug mode **FLASK_DEBUG=1  FLASK_APP=app.py flask run**


## Running the tests

> To perform the test of the project simultaneously:

   **pytest**

> To perform a test at a time:

   **pytest test_items.py**
   **pytest test_orders.py**
   **pytest test_users.py**