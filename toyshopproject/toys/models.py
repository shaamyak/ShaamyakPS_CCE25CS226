from django.db import models
from django.contrib.auth.models import User

class Toy(models.Model):
    toy_name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    price = models.CharField(max_length=20)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.toy_name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        try:
            return float(self.price_numeric()) * self.quantity
        except (ValueError, TypeError):
            return 0.0

    def price_numeric(self):
        try:
            return float(''.join(c for c in str(self.toy.price) if c.isdigit() or c == '.'))
        except (ValueError, TypeError):
            return 0.0

    def __str__(self):
        return f"{self.user.username} - {self.toy.toy_name} ({self.quantity})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Profile of {self.user.username}"
