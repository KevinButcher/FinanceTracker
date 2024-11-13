from django import forms
from .models import Transaction, Category, Month

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'month', 'amount', 'description']
