from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from . import views
from .views_api import StudentViewSet, ProductViewSet , AmountInsertedViewSet, ChangeReturnViewSet, OrderViewSet

# --- Normal (HTML) views ---
html_urlpatterns = [
    path('', views.home, name='home'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('balance/', views.balance_page, name='balance_page'),
    path('receipt/', views.receipt, name='receipt'),
]

# --- API routes ---
router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'products', ProductViewSet)
router.register(r'amountinserted', AmountInsertedViewSet)
router.register(r'changereturn', ChangeReturnViewSet)
router.register(r'orders', OrderViewSet)

api_urlpatterns = [
    path('api/', include(router.urls)),
]

# --- Combine both ---
urlpatterns = html_urlpatterns + api_urlpatterns

# --- Media/static in debug mode ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
