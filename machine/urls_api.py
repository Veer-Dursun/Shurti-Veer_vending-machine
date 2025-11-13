from rest_framework import routers
from .views_api import StudentViewSet, ProductViewSet  , AmountInsertedViewSet, ChangeReturnViewSet, OrderViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'products', ProductViewSet)
router.register(r'amountinserted', AmountInsertedViewSet)
router.register(r'changereturn', ChangeReturnViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls
