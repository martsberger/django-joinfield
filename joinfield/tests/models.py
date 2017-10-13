from django.db import models


class Surname(models.Model):
    name = models.CharField(primary_key=True, max_length=75)


class Person(models.Model):
    first_name = models.CharField(max_length=75)
    last_name = models.JoinField(Surname, on_delete=models.DO_NOTHING, name='last_name')