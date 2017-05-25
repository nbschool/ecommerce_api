Developing new Resources
========================

Each `Resource` is described by:

* a ``Model``: describes the resource structure, generates and handles the database table and allows querying data.
* a ``Schema``: is used to generate a jsonapi compliant representation of a resource and to validate client's requests data.
* a ``View``: exposes the resource, through our REST API built with `flask-restful`, to clients.

To create a completely working resource all of those three should be exists and work together.


Creating a Resource model
---------------------------

.. NOTE::
    Models implements `Peewee ORM <https://github.com/coleifer/peewee>`_, so for specific documentation
    about fields and methods refer to their `documentation page <http://docs.peewee-orm.com/en/latest/>`_.

All our resource models extend :any:`BaseModel`, that implements all the required logic for parsing,
validating - including fallback values - default common attributes and some override of `peewee` methods.

Every resource is as purely descriptive as possibile, but can implement `resource-specific` methods
(see for example :class:`models.User` or :class:`models.Order`).

Creating a new simple resource is then as easy as:

.. code-block:: python

    class MyResource(BaseModel):
        my_attribute = CharField()


Creating a Resource schema
--------------------------

.. TODO:: 

    * Brief jsonapi intro
    * How to create a schema and link it

Schemas are built upon `Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ and
`Marshmallow JSONAPI <http://marshmallow-jsonapi.readthedocs.io/>`_, to allow proper
implementation of the `JSONAPI Standards <http://jsonapi.org>`_.

Technically speaking `schemas` don't know how they will be used or where, but each schema is meant to
work with a specific model and extracts and validates data in - and for - that specific model.

For this reason each schema *should* be named after the model that will implement it, so :class:`models.User` will
implement :class:`schemas.UserSchema` and so on.

Similarly to the :mod:`models`, all the logic required inside a schema is inside their base class :class:`schemas.BaseSchema`
and every schema **must** extend it to properly function.

.. NOTE::
    Due to issues with the :any:`decimal.Decimal` objects that the :mod:`json` module from the standard library cannot parse,
    every schemas that implement those **must** use `simplejson` ``json_module = simplejson`` attribute to its ``Meta`` class.
    This is recommended in any case but required for those field types that `json` cannot parse correctly.

Creating a new schema is then as simple as

.. code-block:: python

    class MySchema(BaseSchema):
        class Meta:
            json_module = simplejson

        attribute = fields.Str(attribute='my_attribute')

Please refer to the documentation of `marshmallow` and `marshmallow-jsonapi` for a full documentation
about fields and Relationships ane ``Meta`` class, required to generate links.


Integrating with models
^^^^^^^^^^^^^^^^^^^^^^^

All the logic required to implement a schema in a model is already present inside the :any:`BaseModel` class. The model itself
only needs to specify the `schema` class through the private attribute ``_schema`` like.

.. code-block:: python

    from schemas import MySchema

    class MyModel(BaseModel):
        my_attribute = CharField()
        _schema = MySchema

.. NOTE::
    If a schema is not provided :any:`BaseSchema` will be used instead to avoid exceptions,
    and you can override the ``json`` method of the `Model` to return a json compatible structure or directly a `string`.
    **NOTE** that this is not recommended since our API relies on schemas for validation and output generation, but is permitted while
    developing new resources.

    .. code-block:: python

        class MyModel(BaseModel):
            my_attribute = CharField()

            def json(self, include_data=[]):
                return json.dumps({
                    attribute: self.my_attribute,
                })


Creating a Resource view
------------------------

Views are built with `Flask <http://flask.pocoo.org>`_ and `Flask Restful <https://flask-restful.readthedocs.io>`_.

Each view module relates to a specific Model and contains all the Resource endpoints to access that given resource.

When present, each view implements validation and output generation from the `schemas`, through the `Model`'s methods.

.. code-block:: python
    :emphasize-lines: 3,9,17

    class MyModelsHandler(Resource):
        def get(self):
            return utils.generate_response(data, OK)
        
        def post(self):
            # get the data from the request
            data = request.get_json()

            errors = MyModel.validate_input(data)
            if errors:
                return errors, BAD_REQUEST

            new_resource = MyModel.create(
                # create the resource with post data
            )

            return utils.generate_response(new_resource.json(), OK)

There are a couple of things to notice here:

1. The request data is validated through the :py:meth:`validate_input` method, that calls the `schema` validation on the
   parsed `request.data`. If there errors are found during validation, they should be returned with a ``BAD_REQUEST`` status
   code, since the request was badly formatted, missing or invalid data and could probably cause an internal server error later
   on.

2. The response is generated through tue :any:`utils.generate_response` function, that takes a `stringified` data and a status code.
   This is needed due to `flask-restful` automation takes the return value of the endpoints (like the ``return errors, BAD_REQUEST``)
   and parses the `data` through a json parser.
   
   Since we already did that with our ``json`` method, we need to create a valid ``Response`` object manually, specifying the correct
   `mime-type`. The utility function serves that purpose


Requiring authorization
-----------------------

To implement the authorization on the endpoint, allowing user's to access only their resources (i.e.
`profile`, `orders` etc, is as simple as importing ``auth`` from :mod:`auth` module and using the
``@auth.login_required`` decorator on the desired resource method (i.e. `GET`).

The currently authorized user can be found in :any:`Auth.current_user`

Assuming that we added a Relationship to ``MyModel``, pointing to a ``User`` model, we can then do

.. code-block:: python

    from auth import auth

    class MyModelHandler(Resource):

        @auth.login_required
        def get(self):
            objs = MyModel.get().where(MyModel.user == auth.current_user)

            return generate_response(MyModel.json_list(objs), 200)



Full Example
------------

.. code-block:: python

    import uuid

    from flask import request
    from flask_restful import Resource
    from marshmallow_jsonapi import fields
    from marshmallow import validate
    from peewee import BooleanField, CharField, ForeignKey, UUIDField

    from auth import auth
    from models import BaseModel
    from schemas import BaseSchema

    # Schema definition should go inside ./schemas.py
    # Schema for the User is omitted for brevity but should exist.

    class MySchema(BaseSchema):
        class Meta:
            type_ = 'mymodel'
            self_url_many = '/mymodel/'
            json_module = simplejson

        id = fields.Str(dump_only=True, attribute='uuid')
        attribute = fields.Str(
            required=True,
            validate=validate.Length(min=1, error='Field should not be blank'),
        )

    # model should go in ./models.py

    class User(BaseModel):
        uuid = UUIDField(unique=True, default=uuid.uuid4)
        email = Charfield()
        password = CharField()
        admin BooleanField(default=False)

    class MyModel(BaseModel):
        _schema = MySchema

        uuid = UUIDField(unique=True, default=uuid.uuid4)
        my_attribute = CharField()
        user = ForeignKey(User, related_name='mymodel')


    # setup the view in views/myview.py

    class MyModelHandler(Resource):
        @auth.login_required
        def get(self):
            objects = MyModel.select().where(MyModel.user == auth.current_user)

            return generate_response(MyModel.json_list(objects), 200)
        
        @auth.login_required
        def post(self):
            # only admin users should be able to post new resources
            if not auth.current_user.admin:
                return None, 401

            data = request.get_json(force=True)
            
            errors = MyModel.validate_input(data)
            if errors:
                return errors, 400
            
            obj = MyModel.create(
                # unsafe, just for example
                attribute=data.get('attribute'),
            )

            return generate_response(obj.json(), 201)


    # Inside app.py the resource should be added with

    api.add_resource(MyModelHandler, '/mymodel/')


This is one of the simplest example that can be done to create a simple resource that can use auth.

In this case the ``validate_input`` can return errors when the `request.data` is malformed
- meaning that does not respects jsonapi standards, like it does not have the `data` root
attribute - or, since we added a validation rule to ``attribute``, will return an error if:


* the attribute is missing (required is defined)
* the attribute type does not match (we want a string)
* the length of the attribute is less than 1 (empty string)

After the login succeded, :any:`Auth.current_user` contains the actual currently logged :any:`User`
instance, so any attribute or method in that class can be easily accessed through that.
