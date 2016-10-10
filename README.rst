django-collectionfield
======================

.. image:: https://api.travis-ci.org/escer/django-collectionfield.svg?branch=master
   :target: https://travis-ci.org/escer/django-collectionfield
.. image:: https://img.shields.io/pypi/v/django-collectionfield.svg
   :target: https://pypi.python.org/pypi/django-collectionfield
.. image:: https://coveralls.io/repos/github/escer/django-collectionfield/badge.svg?branch=master
   :target: https://coveralls.io/github/escer/django-collectionfield?branch=master

A reusable Django model field to store collections.

Features
--------

- highly configurable **model field** (changing collection and item types, sorting, choices, item uniqueness and more)
- **custom lookups** to simplify queries over collection items
- **form fields** for working with collections
- collection **item validators**
- extended ``get_FIELD_display`` method for model fields with choices
- works with database backends without native support for multi-value columns (like ArrayField for PostgreSQL)

Installation
------------

.. code-block:: python

   pip install django-collectionfield
   

Usage
-----

Model field
~~~~~~~~~~~

Define model with field that stores lists of strings:

.. code-block:: python

   # models.py
   from django.db import models
   from collectionfield.models import CollectionField
   
   class MyModel(models.Model):
       tags = CollectionField()

Pass values to model field:

.. code-block:: python

   my_model = MyModel.objects.create(tags=['test', 'values'])
   my_model.values
   ['test', 'values']

Making queries
~~~~~~~~~~~~~~

Retrieve model instances with particular value present in the collection:

.. code-block:: python

   MyModel.objects.filter(tags__has='test')

Retrieve model instances with *ALL* values present in the collection (ignoring items' order):

.. code-block:: python

   MyModel.objects.filter(tags__hasall=['test', 'values'])

Retrieve model instances with *ANY* of values present in the collection:

.. code-block:: python

   MyModel.objects.filter(tags__hasany=['test', 'values'])


Customizing collections
~~~~~~~~~~~~~~~~~~~~~~~

Custom collection and item type:

.. code-block:: python

   class IntegerSet(models.Model):
       # This field will provide sets of integers 
       # instead of default lists of strings:
       values = CollectionField(collection_type=set, item_type=int)

Sorting and uniqueness:

.. code-block:: python

   class SortedUniqueTextList(models.Model):
       # Before saving, items will be sorted and duplicates dropped:
       texts = CollectionField(sort=True, unique_items=True)

Choices and collection size limit:

.. code-block:: python

   class TaggedModel(models.Model):
       tags = CollectionField(
           # Both choices and max_items limit are checked during model validation.
           choices=(
               ('action', "Action"),
               ('comedy', "Comedy"),
               ('horror', "Horror"),
               # ...
           ),
           max_items=2
       )

``get_FIELD_display`` method can handle multiple choices and provide options to customize the display:

.. code-block:: python

   tagged_model = TaggedModel.objects.create(tags=['action', 'horror'])
   tagged_model.get_tags_display()
   "Action, Horror"
 
   def li_mapper(value, label):
       return "<li>{0}</li>".format(label)
    
   def ul_wrapper(field_display):
       return "<ul>{0}</ul>".format(field_display)

   tagged_model.get_tags_display(delimiter='', mapper=li_mapper, wrapper=ul_wrapper)
   '<ul><li>Action</li><li>Horror</li></ul>'

Django built-in validators work with entire field values. ``django-collectionfield`` provide validation of single collection items:

.. code-block:: python

   from collectionfield.validators import (
       ItemMinValueValidator, ItemMaxValueValidator
   )

   class IntegerList(models.Model):
       values = CollectionField(
           item_type=int,
           # item validators check each item separately:
           validators=[ItemMinValueValidator(1), ItemMaxValueValidator(5)]
       )

Form fields
~~~~~~~~~~~

``django-collectionfield`` comes with 2 form fields:

.. code-block:: python

   from collectionfield.forms import CollectionField, CollectionChoiceField

   # ``collectionfield.forms.CollectionField`` converts comma-separated text
   # into collection of values:

   class MyForm(forms.Form):
       values = CollectionField()

   my_form = MyForm({'values': "A, B, C"})
   my_form.is_valid()
   True
   my_form.cleaned_data['values']
   ['A', 'B', 'C']

   # ``collectionfield.forms.CollectionChoiceField`` behaves more like 
   # regular MultipleChoiceField:

   class MyChoiceForm(forms.Form):
      values = CollectionChoiceField(
          choices=(
              ('action', "Action"),
              ('comedy', "Comedy"),
              ('horror', "Horror"),
              # ...
          )
      )

   my_choice_form = MyChoiceForm({'values': ['action', 'comedy']})
   my_choice_form.is_valid()
   True
   my_choice_form.cleaned_data['values']
   ['action', 'comedy']

Both form fields support the same set of parameters as the model field:

.. code-block:: python

   from collectionfield.forms import CollectionField

   class MyForm(forms.Form):
       values = CollectionField(collection_type=set, item_type=int)

   my_form = MyForm({'values': "1, 2, 1, 3"})
   my_form.is_valid()
   True
   my_form.cleaned_data['values']
   {1, 2, 3}

Representation in database
~~~~~~~~~~~~~~~~~~~~~~~~~~

CollectionField converts its values into string of up to 1024 characters using the following format:

.. code-block:: python

   "|item1|item2|item3|"

Default delimiter ('|') and maximum length can be configured:

.. code-block:: python

   class MyModel(models.Model):
       values = CollectionField(delimiter="$", max_length=2000)

Requirements
------------

Python: 2.7, 3.4, 3.5

Django: 1.8, 1.9, 1.10

.. TODO: Changes