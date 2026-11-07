from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toys/', views.toy_list, name='toy_list'),
    path('toys/add/', views.add_toy, name='add_toy'),
    path('toys/edit/<int:id>/', views.edit_toy, name='edit_toy'),
    path('toys/delete/<int:id>/', views.delete_toy, name='delete_toy'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
