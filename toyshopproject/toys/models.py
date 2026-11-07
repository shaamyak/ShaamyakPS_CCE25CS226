from django.db import models

# Model to store toy inventory details in the database
class Toy(models.Model):
    # Field to store the name of the toy
    toy_name = models.CharField(max_length=100)

    # Field to store the age group (e.g. 3-5 Years)
    age_group = models.CharField(max_length=50)

    # Field to store category (e.g. Board Games, Action Figures)
    category = models.CharField(max_length=50)

    # Field to store price (stored as CharField as required)
    price = models.CharField(max_length=20)

    # This method returns the toy name when the object is printed
    def __str__(self):
        return self.toy_name
