Introduction to the developer's guide
==============================

This section explains how to contribute to the project, specifically *how things work*,
such as schemas and models integration, how to develop new tests, setup views and substantially not mess things up.

.. TODO:: Get here everything that is a *how to*

.. contents:: :local:

Running dev server
------------------

Development server can be run either directly with flask or with gunicorn through the heroku integration.

After setting up your ``.env`` file, the development server can be run with ``heroku local -f Procfile.dev``

.. code-block:: none

    FLASK_APP=app.py
    FLASK_DEBUG=1
