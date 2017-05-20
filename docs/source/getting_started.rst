Getting started
===============

Getting started with the project is pretty straightforward.

Installing
----------

``pip install -r requirements.txt``


Running the server
------------------

Server can be run with

* flask using ``Flask_APP=app.py flask run`` 
* gunicorn, through heroku, using ``heroku local``

.. NOTE::
    using heroku requires to setting up your ``.env`` file.

    .. code-block:: none

        FLASK_APP=app.py




