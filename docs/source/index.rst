.. E-Commerce documentation master file, created by
   sphinx-quickstart on Fri May 19 11:41:19 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction to E-Commerce
======================================

.. TODO::

  * Define the various sections of the documentation
  * Complete other todos
  * Write proper docstrings
  * Define static pages for *how to* (new schemas/models, integration, testing)
  * Testing documentation
  * Introduction section for the whole documentation
  * Heroku integration
  * Cleanup readme

REST API for an e-commerce platform, created as a class project.

The project relies on

* `Peewee <http://docs.peewee-orm.com/en/latest/>`_ for the ORM
* `Flask <http://flask.pocoo.org>`_ and
  `Flask Restful <https://flask-restful.readthedocs.io>`_ for the views
* `Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ and
  `Marshmallow JSONAPI <http://marshmallow-jsonapi.readthedocs.io/>`_ for
  integration with the `JSONAPI Standards <http://jsonapi.org>`_

For specifics about the implemented functionalies or to extend the API refer to
the linked documentation and specifications.

.. toctree::
   :maxdepth: 2
   :caption: Content

   getting_started
   dev_guide/index
   doc_contrib
   heroku_integration
   api/index




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
