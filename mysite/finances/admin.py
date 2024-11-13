from django.contrib import admin
from .models import Category, Month, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Month)