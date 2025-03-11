from django.db import models


class Model1(models.Model):
    name = models.CharField(max_length=100)


class Model2(models.Model):
    name = models.CharField(max_length=100)


class Model3(models.Model):
    name = models.CharField(max_length=100)
