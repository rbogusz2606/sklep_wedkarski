from django.db import models
from django.contrib.auth.models import User
from app .models import Product

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    adress = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country= models.CharField(max_length=100)

    def __str__(self):
        return f'ADRES: {self.adress} || USER: {self.user}'
    
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Oczekujące'),
        ('paid', 'Zapłacone'),
        ('failed', 'Nieudane'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zamówienie {self.order_number} przez {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Cena jednostkowa

    def __str__(self):
        return f"{self.quantity} x {self.product.name} w zamówieniu {self.order.order_number}"