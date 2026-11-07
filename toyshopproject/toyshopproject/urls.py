from django.contrib import admin
from django.urls import path, include

# Main URL configuration
urlpatterns = [
    # Django admin portal
    path('admin/', admin.site.urls),

    # Include all URLs from the toys app
    path('', include('toys.urls')),
]
