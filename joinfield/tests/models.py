from django.db import models

from joinfield.joinfield import JoinField


class Surname(models.Model):
    name = models.CharField(primary_key=True, max_length=75)


class Person(models.Model):
    first_name = models.CharField(max_length=75)
    last_name = JoinField(Surname, on_delete=models.DO_NOTHING)
