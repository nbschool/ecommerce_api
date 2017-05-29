Pytest stuff
============

.. TODO:: Fix RESULTS annotation


Tests Base Class
----------------

.. automodule:: tests.test_case
    :members:
    :exclude-members: TABLES

.. autoattribute:: tests.test_case.TABLES
    :annotation: = [<Model classes>]

    Contains all the models that extend :any:`BaseModel` that are used in testing,
    allowing modifications required for testing.

    .. NOTE::

        This variable should be extended each time a new model is created


General utility module
----------------------

.. automodule:: tests.test_utils
    :members:
    :exclude-members: RESULTS

.. autoattribute:: tests.test_utils.RESULTS
    :annotation: = Parsed expected_results.json

    When the module is initialized this will be populated by a ``json.load``
    of the ``expected_results.json`` file

Pytest configuration module
---------------------------

.. automodule:: tests.conftest
    :members: