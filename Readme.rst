.. image:: https://travis-ci.org/martsberger/django-joinfield.svg?branch=master
    :target: https://travis-ci.org/martsberger/django-joinfield

Django JoinField
================

This package provides a field type for Django models that allows
joins to a related model without a foreign key.

Quickstart
----------

Install via pip::

    pip install django-joinfield

Put ``joinfield`` in INSTALLED_APPS in your settings file. Then you can import
JoinField and use it when defining your models::

    from joinfield.joinfield import JoinField

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

Examples
--------

Let's imagine a database of people and family information. One table might
contain general family information keyed by Surname::

    class Surname(models.Model):
        name = models.CharField(max_length=32, primary_key=True)
        crest = models.ImageField(...)
        references = models.ManyToManyField('FamilyDocuments', ...)
        origin = models.ForeignKeyField('Country')

A separate table contains the individual people. Each person has a last name
and if that last name corresponds to a Surname in the Surname table, we want
to be able to join from Person to Surname. However, not every person's last
name will correspond to a Surname that we have detailed information for. So
we don't want to require a record in the Surname table in order to create a
Person. The person class will use the JoinField::

    class Person(models.Model):
        first_name = models.CharField(max_length=32)
        last_name = JoinField(Surname, on_delete=models.DO_NOTHING)

This will result in the database column for Person.last_name being a CharField
just like it is defined on Surname.name.

A Person object can be created by assigning either a Surname object or a
literal value to the last_name attribute::

    # Create a Person object with a literal value for last name
    Person.objects.create(first_name='Jon', last_name='Doe')

    # A Surname object can be created after the fact
    doe = Surname.objects.create(name='Doe')

    # A person can be created by passing a Surname object as the last_name
    Person.objects.create(first_name='Jane', last_name=doe)

The ORM can be used for both forward and reverse relationships::

    # These two queries are equivalent
    Person.objects.filter(last_name='Doe')  # literal filter
    Person.objects.filter(last_name=doe)  # filter on forward relationship

    # The reverse relationship can also be used for filtering
    Surname.objects.filter(person__first_name='Jon')

    # And annotations
    Surname.objects.annotate(count=Count('person'))

The ``_id`` field
-----------------

Other than the lack of database constraints (which provides the ability to
assign a literal in addition to an instance), the JoinField is very much
like a ForeignKey field. The value that is stored in the database is the
literal value assigned or the value of the field on the instance we join to.
When an instance is retrieved, the attribute defined as a JoinField will have
the instance we join to as it's value. An additional attribute with "_id"
appended stores the literal value.

From the example above, when a Person instance is retrieved, the last_name
attribute will be a Surname instance and the last_name_id attribute will be
the actual value of the last_name. For Person instances that don't join to
any value in the Surname table (not valid for ForeignKey), the last_name
attribute will be None and the last_name_id attribute will still have the
literal last_name value.

For example::

    jon = Person.objects.get(first_name='Jon', last_name='Doe')
    print (jon.first_name, jon.last_name, jon.last_name_id)

Will print the following::

    (u'Jon', <Surname: Surname object>, u'Doe')

And if we create a Person with no Surname::

    james = Person.objects.create(first_name='James', last_name='Smith')
    print (james.first_name, james.last_name, james.last_name_id)

prints the following::

    (u'James', None, u'Smith')

License
-------

MIT

Copyright 2023 Brad Martsberger

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.