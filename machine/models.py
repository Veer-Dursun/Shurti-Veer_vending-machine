from django.db import models
from django.utils import timezone

#  Student 
class Student(models.Model):
    CAMPUS_CHOICES = [
        ('Ebene', 'Ebene'),
    ]

    name = models.CharField(max_length=100)
    campus = models.CharField(max_length=50, choices=CAMPUS_CHOICES)
    join_in = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.campus}"


#  Product 
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Cake', 'Cake'),
        ('Soft Drink', 'Soft Drink'),
    ]

    product_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.category})"


# Amount Inserted 
class AmountInserted(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    notes_200 = models.PositiveIntegerField(default=0)
    notes_100 = models.PositiveIntegerField(default=0)
    notes_50 = models.PositiveIntegerField(default=0)
    notes_25 = models.PositiveIntegerField(default=0)
    coins_20 = models.PositiveIntegerField(default=0)
    coins_10 = models.PositiveIntegerField(default=0)
    coins_5 = models.PositiveIntegerField(default=0)
    coins_1 = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    denominations = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        self.total_amount = (
            self.notes_200*200 + self.notes_100*100 + self.notes_50*50 + self.notes_25*25 +
            self.coins_20*20 + self.coins_10*10 + self.coins_5*5 + self.coins_1*1
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - Rs {self.total_amount}"


#Change Return 
class ChangeReturn(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    notes_200 = models.PositiveIntegerField(default=0)
    notes_100 = models.PositiveIntegerField(default=0)
    notes_50 = models.PositiveIntegerField(default=0)
    notes_25 = models.PositiveIntegerField(default=0)
    coins_20 = models.PositiveIntegerField(default=0)
    coins_10 = models.PositiveIntegerField(default=0)
    coins_5 = models.PositiveIntegerField(default=0)
    coins_1 = models.PositiveIntegerField(default=0)
    total_return = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    denominations = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        self.total_return = (
            self.notes_200*200 + self.notes_100*100 + self.notes_50*50 + self.notes_25*25 +
            self.coins_20*20 + self.coins_10*10 + self.coins_5*5 + self.coins_1*1
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - Rs {self.total_return}"


#  Order 
class Order(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_inserted = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student.name} - Rs {self.total_purchase} (Change: Rs {self.change_amount})"
