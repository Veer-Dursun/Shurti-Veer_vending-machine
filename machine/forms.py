from django import forms
from .models import Student

class StudentLoginForm(forms.Form):
    name = forms.CharField(
        label='Your Name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    campus = forms.ChoiceField(
        label='Select Campus',
        choices=Student.CAMPUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    inserted_money = forms.DecimalField(
        label='Money Inserted (Max Rs 200)',
        max_digits=6,
        decimal_places=2,
        max_value=200,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
