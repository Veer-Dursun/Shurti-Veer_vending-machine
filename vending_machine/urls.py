from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('machine.urls')),  # ← ONLY THIS FOR ROOT PATH
]