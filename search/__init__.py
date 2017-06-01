"""
Full text search engine for the application database.


Introduction
------------

Main functionality is exposed through :func:`search.core.search` that can be
imported directly from search as in

.. code-block:: python

    from search import search
    results = search('query', ['attr'], MyModel)

.. note::
    This is a simple search algorithm that implements just a few checks
    and while it tries to do a full text search in an efficient way, as of now
    it cannot be relied upon with the utmost certainty.

    This piece of code is in a developing stage and will most probably removed
    from the final implementation of the search in favor of other libraries such
    as `Whoosh <https://goo.gl/hGs11I>`_.

In any case, for simple queries on fairly simple dataset, the algorithm behaves
quite nice. Any implementation, suggestions and fixes - and most of all testing
is welcome from everybody.


Algorithm
^^^^^^^^^

Basic search functionality tries to do a `sort-of` full text search that relies
on the `Jaro-Winkler <https://goo.gl/b59g4v>`_ algorithm to calculate the
distance between words in a matrix `query * term`, the `movement cost` for each
word in the phrases (words not where they should be have less value) and on a
weigth value when searching through multiple model attributes.

Since I'm no mathematician I can't actually put down a formula for you, sorry.
Feel free to check the code and come up with something :)


Implementing
^^^^^^^^^^^^

This functionality, as of now, works on any iterable of object that are created
with a class that implements a ``select()`` method as ``staticmethod`` that
returns an iterable of object of that class, without any condition, since
it's been designed to work with peewee models and iterate every table dataset
on each query (simplest integration) so for now this will do for us.

Later on - as in: when and if we implement it directly into the models - we
may switch to receive an iterable of object instead of a class, but for now
to use with any other type of object a solution could be something like:

.. code-block:: python

    class MyClass:
        instances = []
        def __init__(self, v):
            self.v = v
            MyClass.instances.append(self)

        @staticmethod
        def select():
            return MyClass.instances

Then it can be used as the first example on the page.


Tweaking
^^^^^^^^

Basic algorithm configuration can be found in :any:`search.config`, that allows
some tweaking on how it filters words and weights stuff.

"""

from search.core import search  # noqa: F401
