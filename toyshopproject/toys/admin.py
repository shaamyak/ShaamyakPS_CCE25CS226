from django.contrib import admin
from .models import Toy, CartItem, Order, UserProfile

admin.site.register(Toy)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(UserProfile)
