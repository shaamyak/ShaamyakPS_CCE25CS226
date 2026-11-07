from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/status/<int:order_id>/', views.admin_update_order_status, name='admin_update_order_status'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),

    path('toys/', views.toy_list, name='toy_list'),
    path('toys/add/', views.add_toy, name='add_toy'),
    path('toys/edit/<int:id>/', views.edit_toy, name='edit_toy'),
    path('toys/delete/<int:id>/', views.delete_toy, name='delete_toy'),
    path('toys/detail/<int:id>/', views.toy_detail, name='toy_detail'),

    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:toy_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.place_order, name='place_order'),
    path('buy-now/<int:toy_id>/', views.buy_now, name='buy_now'),
    path('orders/', views.user_orders, name='user_orders'),
    path('profile/', views.user_profile, name='user_profile'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
