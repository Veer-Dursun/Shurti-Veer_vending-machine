from rest_framework import serializers
from .models import Student, Product, AmountInserted, ChangeReturn, Order

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class AmountInsertedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountInserted
        fields = '__all__'

class ChangeReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeReturn
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
