from django.db.models import Count
from django.test import TestCase

from joinfield.tests.models import Person, Surname


class Tests(TestCase):

    def test_join_field(self):
        # Create a child object with no related object parent
        Person.objects.create(first_name='Jon', last_name='Doe')

        # We can retrieve this object from the database
        jon_doe = Person.objects.get(first_name='Jon', last_name='Doe')
        self.assertIsNone(jon_doe.last_name)
        self.assertEqual(jon_doe.last_name_id, 'Doe')

        # Create a parent object corresponding to the existing child
        doe = Surname.objects.create(name='Doe')

        jon_doe = Person.objects.get(first_name='Jon', last_name='Doe')
        self.assertEqual(jon_doe.last_name, doe)
        self.assertEqual(jon_doe.last_name_id, 'Doe')

        # Create a child object with a related instance assigned to join field
        jane_doe = Person.objects.create(first_name='Jane', last_name=doe)

        self.assertEqual(jane_doe.last_name, doe)
        self.assertEqual(jane_doe.last_name_id, 'Doe')

    def test_join_field_forward_filter(self):
        doe = Surname.objects.create(name='Doe')
        jon = Person.objects.create(first_name='Jon', last_name='Doe')
        jane = Person.objects.create(first_name='Jane', last_name='Doe')

        does = Person.objects.filter(last_name='Doe')
        self.assertQuerysetEqual(does, [repr(jon), repr(jane)], ordered=False)

        jamal = Person.objects.create(first_name='jamal', last_name=doe)

        does = Person.objects.filter(last_name='Doe')
        self.assertQuerysetEqual(does, [repr(jon), repr(jane), repr(jamal)], ordered=False)

        does = Person.objects.filter(last_name=doe)
        self.assertQuerysetEqual(does, [repr(jon), repr(jane), repr(jamal)], ordered=False)

    def test_join_field_reverse_filter(self):
        doe = Surname.objects.create(name='Doe')
        smith = Surname.objects.create(name='Smith')

        Person.objects.create(first_name='Jon', last_name=doe)
        Person.objects.create(first_name='Jane', last_name=doe)
        Person.objects.create(first_name='Jack', last_name=smith)

        surnames = Surname.objects.filter(person__first_name='Jon')
        self.assertQuerysetEqual(surnames, [repr(doe)], ordered=False)

    def test_join_field_annotate(self):
        doe = Surname.objects.create(name='Doe')
        smith = Surname.objects.create(name='Smith')

        Person.objects.create(first_name='Jon', last_name=doe)
        Person.objects.create(first_name='Jane', last_name=doe)
        Person.objects.create(first_name='Jack', last_name=smith)

        surname_counts = Surname.objects.annotate(count=Count('person'))
        expected_surname_counts = {
            'Doe': 2,
            'Smith': 1
        }

        for surname in surname_counts:
            self.assertEqual(surname.count, expected_surname_counts[surname.name])

    def test_join_field_child_set(self):
        Surname.objects.create(name='Doe')
        Surname.objects.create(name='Smith')

        jon = Person.objects.create(first_name='Jon', last_name='Doe')
        jane = Person.objects.create(first_name='Jane', last_name='Doe')
        Person.objects.create(first_name='Jack', last_name='Smith')

        doe = Surname.objects.get(name='Doe')

        does = doe.person_set.all()

        self.assertQuerysetEqual(does, [repr(jon), repr(jane)], ordered=False)

    def test_join_field_delete(self):
        doe = Surname.objects.create(name='Doe')
        smith = Surname.objects.create(name='Smith')

        Person.objects.create(first_name='Jon', last_name=doe)
        Person.objects.create(first_name='Jane', last_name=doe)
        Person.objects.create(first_name='Jack', last_name=smith)

        # Deleting a Surname should not delete a Person pointing at it
        self.assertEqual(Surname.objects.count(), 2)
        self.assertEqual(Person.objects.count(), 3)

        jon = Person.objects.get(first_name='Jon', last_name='Doe')
        self.assertEqual(jon.last_name, doe)
        self.assertEqual(jon.last_name_id, 'Doe')

        doe.delete()

        self.assertEqual(Surname.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 3)

        jon = Person.objects.get(first_name='Jon', last_name='Doe')
        self.assertIsNone(jon.last_name)
        self.assertEqual(jon.last_name_id, 'Doe')
