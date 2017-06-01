Search Engine Package
=====================

Full text search engine for the application database.

.. contents:: :local:

Introduction
------------

Main functionality is exposed through :func:`search.core.search` that can be
imported directly from search as in

.. note::
    This is a simple search algorithm that implements just a few checks
    and while it tries to do a full text search in an efficient way, as of now
    it cannot be relied upon with the utmost certainty.

    This piece of code is in a developing stage and will most probably removed
    from the final implementation of the search in favor of other libraries such
    as `Whoosh <https://goo.gl/hGs11I>`_.

Anyway it can be used to digest any type of object-like collection, as long
as ``getattr(object, '<attribute>')`` returns a value, so for quick search
implementation, as placeholder or for testing purposes it does the trick.


Basic usage
-----------

.. code-block:: python

    from search import search

    collection = Model.select()  # returns an iterable of objects
    results = search('query', ['attr'], collection)



Algorithm
---------

Basic search functionality tries to do a `sort-of` full text search that relies
on the `Jaro-Winkler <https://goo.gl/b59g4v>`_ algorithm to calculate the
distance between words in a matrix `query * term`, the `movement cost` for each
word in the phrases (words not where they should be have less value) and on a
weigth value when searching through multiple model attributes.

Since I'm no mathematician I can't actually put down a formula for you, sorry.
Feel free to check the code and come up with something :)


Tweaking
--------

Basic algorithm configuration can be found in :any:`search.config`, that allows
some tweaking on how it filters words and weights stuff.


E-commerce API implementation
-----------------------------

The package is implemented in our REST API through the database models.
:any:`BaseModel` has a new method (:any:`BaseModel.search`) that wraps the
search functionality on the callee.

By default all the models are not allowed to run a search (calling a
``search()`` raises an :class:`exceptions.SearchAttributeMismatch`).
To `enable` the search functionality there are two class attributes to define:

* ``_search_attributes`` that specifies what fields to look up into
* ``_search_weights`` that specifies the weight of each field. This is optional

.. code-block:: python

    class Item(BaseModel):
        # ...
        _search_attributes = ['name', 'category', 'description']
        _search_weights = [3, 2, 1]  # optional

If the weights are not specified they will be ranked as they appear in the
`_search_attributes` attribute, with first more important.

Another quick option is to pass the attributes to lookup at call time, such as

.. code-block:: python

    result = Item.search('query', Item.select(), limit=10, attributes=['name'])

This will override any existing class attributes that have been setup (no search
into `category` and `description` fields.


APIs
----

search.core
+++++++++++

.. automodule:: search.core
    :members:


search.utils
++++++++++++

.. automodule:: search.utils
    :members:


search.config
+++++++++++++

.. automodule:: search.config
    :members:
