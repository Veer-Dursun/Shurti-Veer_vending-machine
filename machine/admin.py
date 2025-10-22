from django.contrib import admin
from .models import Student, Product, AmountInserted, ChangeReturn, Order

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'campus', 'join_in')
    search_fields = ('name', 'campus')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'category', 'qty', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'product_id')


@admin.register(AmountInserted)
class AmountInsertedAdmin(admin.ModelAdmin):
    list_display = ('student', 'date_time', 'total_amount', 'notes_200', 'notes_100', 'notes_50', 'notes_25',
                    'coins_20', 'coins_10', 'coins_5', 'coins_1')


@admin.register(ChangeReturn)
class ChangeReturnAdmin(admin.ModelAdmin):
    list_display = ('student', 'date_time', 'total_return', 'notes_200', 'notes_100', 'notes_50', 'notes_25',
                    'coins_20', 'coins_10', 'coins_5', 'coins_1')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('student', 'product', 'date_time', 'amount_inserted', 'balance', 'total_purchase')
    list_filter = ('date_time', 'student')
    search_fields = ('student__name', 'product__name')
