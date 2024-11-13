from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category
    
class Month(models.Model):
    month = models.CharField(max_length=20, unique=True)
    year = models.IntegerField()

    class Meta:
        unique_together = ('month', 'year') # ensure unique combinations

    def __str__(self):
        return f"{self.month} {self.year}"
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="transactions")
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #setting blank = True allows field to be optional, and stores an empty string instead of null
    description = models.CharField(max_length=255, blank=True) 
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction by {self.user.first_name} {self.user.last_name} on {self.date.strftime('%Y-%m-%d')}: ${self.amount}"