Getting started
===============

Getting started with the project is pretty straightforward.

Installing
----------

After setting up a ``virtualenv`` to work with, simply do:

.. code-block:: console

    $ pip install -r requirements.txt


Running the server
------------------

Application server can be run either directly from flask or through heroku.

Flask
^^^^^
.. code-block:: console

    $ Flask_APP=app.py flask run

Heroku & Gunicorn
^^^^^^^^^^^^^^^^^

.. TODO::
    .env example

Setup your ``.env`` file with all the needed variables

.. code-block:: none

    FLASK_APP=app.py

then

.. code-block:: console

    $ heroku local

To startup the development server 

.. code-block:: console

    $ heroku local -f Procfile.dev


Running test suite
------------------

Tests are built with ``pytest``, so just execute

.. code-block:: console

    $ pytest

You may also refer to `Pytest documentation <https://docs.pytest.org/>`_
for a complete guide on pytest arguments.