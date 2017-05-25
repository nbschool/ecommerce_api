Developing tests
==================

Our test suite relies on `pytest` and `mocker` to use deterministic values on randomic ones, like
`UUIDs`. This mocking is required due to our jsonapi implementation, that requires a little understaing
on how :any:`assert_valid_response` works.


Tests structure
---------------

Our tests are structured as::

    tests/
        |- conftest.py
        |- test_case.py
        |- expected_results.json
        |- ... <test_units>

Where:

* ``conftest`` contains all the `pytest fixtures` definition. the filename is required by pytest
* ``test_case`` contains our BaseClass for all the test suite, that **must** inherit from it
* ``expected_results`` is a json containing all the jsonapi expected results that the tests must
  validate against
* ``<test_units>`` are single test units, one for each individual resource, that **must** be named
  as ``test_<resource name>`` in order for pytest to find them.


Data mocking
------------

In short:

* Every field can be manually specified with static data
* If not specified, the ``uuid`` field of the Models will be generated using :any:`mock_uuid_generator`
  that will reset on every new test function and generates UUID in the form of
  ``00000000-0000-0000-0000-000000000001``
* If not specified, the :any:`BaseModel.created_at` attribute will default to
  ``datetime.datetime(2017, 2, 20, 10, 16, 50, 140620)`` for every model instance

This is possible due to the defined fixtures in :any:`conftest`.

.. NOTE::

    As of now user's :any:`User.email` **must** be manually defined since they are not mocked
    and are required to be unique.


Creating new test suites
------------------------

For every new :any:`models` created a new test suite is required, this normally requires a new file
that, following our `MyModel <create_resources.html#full-example>`_ example, should be
named ``test_mymodel.py``.

Each test suite requires a new class with a name that **must** start with ``Test`` - so in our case
it would be natural to call it ``TestMyModel`` - and **must** extend from :any:`TestCase`.

Also, to properly work with the TestCase class, the new model should be added to the 
:any:`test_case.TABLES` list.

.. code-block:: python

    # test_case.py
    from models import MyModel  # Assuming the model exists in models.py

    TABLES = [User, MyModel]  # Assuming no other tables exist

    # test_mymodel.py
    from models import MyModel
    from tests.test_case import TestCase
    from tests import test_utils

    class TestMyModel(TestCase):
        test_example(self):
            user = User.create(email='email@email.com', password='password')
            model = MyModel.create(attribute='hello world', user=user)

            asert Model.select().count == 1

This is all that's needed to create the simplest tests possible


Testing with JSONAPI
--------------------

Things get a little messier when the tests need to use the ``json`` method, either directly or
through the flask endpoints.

This is due to the implementation of the JSONAPI standards through marshmallow-jsonapi that
generates quite long structures and doesn't generate lists (i.e. `included` resources) always in the
same order.

To make up for this, since it makes no sense to use the json method to validate itself,
we created an ``expected_results.json`` file that should contain all the expected
results from a jsonapi output, and a assertative utility (:any:`assert_valid_response`, see below)
that will take care of normalizing both the expected result and the jsonapi output, then assert
their equality.

Expected_results structure
++++++++++++++++++++++++++

The JSON containing the results is structured as::

    <test_file_name>
        |- <optional test_class_name>
            |- <test_method_name>

.. NOTE::

    To avoid redundancy, all the names should **not** have the ``test_`` prefix.

.. code-block:: json

    {
        "mymodel": {
            "get_mymodels__success": [
                {
                    "data": {}
                }
            ]
        },
        "schemas": {
            "mymodel": {
                "json_validation__fail": {
                    "errors": []
                }
            }
        }
    }

The file is automatically loaded in :any:`test_utils.RESULTS` when the testing utility module is loaded.


Validating the test json
++++++++++++++++++++++++

The general idea is that for every test that needs to work with `jsonapi` (either directly or through the
Flask API) a new entry in our `json` file.

To get the entry there are 3 main options:

* Manually write what is expected to be returned - long solution and prone to errors
* use a ``print`` statement to get the expected result directly from the test
  and "`manually`" validate its content (in this case remember the ``-s`` flag for
  pytest in order to pass the print output to sdout)
* use a ``pdb`` call inside the test to get the response and validate it (recommended method)


After the response is what is expected (manually checking its content) it can be copy-pasted inside the json
file.


.. code-block:: python

    # ...

    def test_get_my_models__success(self):

        # Create resources here if needed

        response = self.app.get('/mymodels/')

        import pdb; pdb.set_trace()
        # $ response.data
        # to get the string returned, that in this case should be 
        # the stringified json

        # extract the expected result from the loaded json
        expected_result = test_utils.RESULTS['mymodel']['get_my_model__success']

        # are the structures equal?
        assert_valid_response(response.data, expected_result)

        # other assertions can be done as usual, obviously
        assery MyModel.select().count == 1


That's it.

:any:`assert_valid_response` will take care of normalizing the two structures, sorting lists in the same
way - due to marshmallow-jsonapi generating them "at random" - and will assert their equality, raising
pytest errors as usual if any found.


Full Example
------------

.. TODO:: Write a full example similar to how to create resources