# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from machine.models import Order, ChangeReturn, AmountInserted
from decimal import Decimal