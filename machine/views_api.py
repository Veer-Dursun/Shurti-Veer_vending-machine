from rest_framework import viewsets
from .models import Student, Product, AmountInserted, ChangeReturn, Order
from .serializers import (
    StudentSerializer, ProductSerializer,
    AmountInsertedSerializer, ChangeReturnSerializer, OrderSerializer
)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AmountInsertedViewSet(viewsets.ModelViewSet):
    queryset = AmountInserted.objects.all()
    serializer_class = AmountInsertedSerializer

class ChangeReturnViewSet(viewsets.ModelViewSet):
    queryset = ChangeReturn.objects.all()
    serializer_class = ChangeReturnSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
