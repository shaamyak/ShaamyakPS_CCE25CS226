from django.urls import path
from . import views

# List of URL routes for the toys application
urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Toy management routes
    path('toys/', views.toy_list, name='toy_list'),
    path('toys/add/', views.add_toy, name='add_toy'),
    path('toys/edit/<int:id>/', views.edit_toy, name='edit_toy'),
    path('toys/delete/<int:id>/', views.delete_toy, name='delete_toy'),

    # User authentication routes
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

