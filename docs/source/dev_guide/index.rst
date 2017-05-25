Introduction to the developer's guide
=====================================

This section explains how to contribute to the project, specifically *how things work*,
such as schemas and models integration, how to develop new tests, setup views and substantially not mess things up.

.. TODO:: Get here everything that is a *how to*

.. contents:: :local:

Project structure
-----------------

.. code-block:: none

    /
    ├─ docs/                        Documentation
    ├─ scripts/                     admin scripts
    ├─ templates/                   html templates
    ├─ tests/                       test suite and utils
    │   ├─ conftest.py              pytest fixtures configuration
    │   ├─ expected_results.json    tests results for jsonapi
    │   └─ test_utils.py            utilities for testing and mocking
    │
    ├─ views/                       flask resources' endpoints
    ├─ app.py                       app entry point and resource builder
    ├─ auth.py                      http auth module
    ├─ exceptions.py                custom exceptions
    ├─ models.py                    ORM models
    ├─ notifications.py             handlers to notify users
    ├─ schemas.py                   models' schemas for jsonapi validation/output
    ├─ utils.py                     generic utilities for models and flask



Running dev server
------------------

Development server can be run either directly with flask or with gunicorn through the heroku integration.

After setting up your ``.env`` file, the development server can be run with ``heroku local -f Procfile.dev``

.. code-block:: none

    FLASK_APP=app.py
    FLASK_DEBUG=1
