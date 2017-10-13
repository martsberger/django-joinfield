.. image:: https://travis-ci.org/martsberger/django-joinfield.svg?branch=master
    :target: https://travis-ci.org/martsberger/django-joinfield

Django JoinField
================

This package provides a field type for Django models that allows
joins to a related model without a foreign key.

Quickstart
----------

Install via pip:

    pip install django-joinfield

Put ``joinfield`` in INSTALLED_APPS in your settings file. Then you can import
JoinField and use it when defining your models::

    from joinfield import JoinField

    class Parent(models.Model):
        column = models.CharField(max_length=64)


    class Child(models.Model):
        parent = JoinField(Parent, to_field='column')

The database column created in the child table will have the type defined by
the ``to_field`` parent column. In this case, a CharField. It will not be a
foreign key and there will be no database constraints between these
two tables.

Now you can do joins between child and parent using the orm::

    parent = Parent.objects.first()
    children = Child.objects.filter(parent=parent)

    # Or
    children = Child.objects.filter(parent__column='some value')