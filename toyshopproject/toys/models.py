from django.db import models

class Toy(models.Model):
    toy_name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    price = models.CharField(max_length=20)

    def __str__(self):
        return self.toy_name
