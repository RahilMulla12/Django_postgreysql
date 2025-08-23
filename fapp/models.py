from django.db import models
from django.contrib.auth.models import User

class WindowOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_address = models.TextField()   
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=(
            ('Pending', 'Pending'),
            ('Processing', 'Processing'),
            ('Completed', 'Completed'),
        ),
        default='Pending'
    )
    note = models.TextField(blank=True, null=True)

class Window(models.Model):
    order = models.ForeignKey(WindowOrder, on_delete=models.CASCADE, related_name='windows')
    type = models.CharField(max_length=100)
    glass_type = models.CharField(max_length=100, default='Standard')
    width = models.FloatField()
    height = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
