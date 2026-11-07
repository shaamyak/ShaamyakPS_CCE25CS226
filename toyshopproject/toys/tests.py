from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Toy, CartItem, Order, UserProfile

class RoleBasedToyShopTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.normal_user = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='customerpassword'
        )
        self.toy = Toy.objects.create(
            toy_name='Lego Police Car',
            age_group='5-8 Years',
            category='Vehicles',
            price='499',
            description='Exciting police vehicle with mini-figures.'
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Toy Shop Inventory System')
        self.assertContains(response, '2026')

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

        response = self.client.get(reverse('view_cart'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'adminuser',
            'password': 'adminpassword'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

        dashboard_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, 'Admin Dashboard')
        self.assertContains(dashboard_response, 'Administrator')

    def test_normal_user_login_redirects_to_user_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'customer1',
            'password': 'customerpassword'
        })
        self.assertRedirects(response, reverse('user_dashboard'))

        dashboard_response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, 'Welcome, customer1')
        self.assertContains(dashboard_response, 'Customer')
        self.assertContains(dashboard_response, 'Lego Police Car')

    def test_normal_user_blocked_from_admin_urls(self):
        self.client.login(username='customer1', password='customerpassword')

        admin_urls = [
            reverse('admin_dashboard'),
            reverse('admin_orders'),
            reverse('admin_users'),
            reverse('toy_list'),
            reverse('add_toy'),
            reverse('edit_toy', args=[self.toy.id]),
            reverse('delete_toy', args=[self.toy.id]),
        ]
        for url in admin_urls:
            response = self.client.get(url)
            self.assertRedirects(response, reverse('user_dashboard'))

    def test_admin_crud_toys(self):
        self.client.login(username='adminuser', password='adminpassword')

        add_response = self.client.post(reverse('add_toy'), {
            'toy_name': 'Monopoly Board Game',
            'age_group': '8+ Years',
            'category': 'Board Games',
            'price': '899',
            'description': 'Family strategy game.'
        })
        self.assertRedirects(add_response, reverse('toy_list'))
        self.assertTrue(Toy.objects.filter(toy_name='Monopoly Board Game').exists())

        new_toy = Toy.objects.get(toy_name='Monopoly Board Game')
        edit_response = self.client.post(reverse('edit_toy', args=[new_toy.id]), {
            'toy_name': 'Monopoly Deluxe Edition',
            'age_group': '8+ Years',
            'category': 'Board Games',
            'price': '1199',
            'description': 'Deluxe board game.'
        })
        self.assertRedirects(edit_response, reverse('toy_list'))
        new_toy.refresh_from_db()
        self.assertEqual(new_toy.toy_name, 'Monopoly Deluxe Edition')

        del_response = self.client.get(reverse('delete_toy', args=[new_toy.id]))
        self.assertRedirects(del_response, reverse('toy_list'))
        self.assertFalse(Toy.objects.filter(id=new_toy.id).exists())

    def test_user_cart_and_order_flow(self):
        self.client.login(username='customer1', password='customerpassword')

        detail_response = self.client.get(reverse('toy_detail', args=[self.toy.id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Lego Police Car')

        add_cart_response = self.client.post(reverse('add_to_cart', args=[self.toy.id]), {'quantity': 2})
        self.assertRedirects(add_cart_response, reverse('view_cart'))
        self.assertEqual(CartItem.objects.filter(user=self.normal_user).count(), 1)

        cart_response = self.client.get(reverse('view_cart'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, 'Lego Police Car')

        checkout_response = self.client.post(reverse('place_order'))
        self.assertRedirects(checkout_response, reverse('user_orders'))
        self.assertEqual(CartItem.objects.filter(user=self.normal_user).count(), 0)
        self.assertEqual(Order.objects.filter(user=self.normal_user).count(), 1)

        orders_response = self.client.get(reverse('user_orders'))
        self.assertEqual(orders_response.status_code, 200)
        self.assertContains(orders_response, 'Lego Police Car')

    def test_admin_orders_and_status_update(self):
        order = Order.objects.create(
            user=self.normal_user,
            toy=self.toy,
            quantity=1,
            total_price=499,
            status='Placed'
        )

        self.client.login(username='adminuser', password='adminpassword')
        orders_page = self.client.get(reverse('admin_orders'))
        self.assertEqual(orders_page.status_code, 200)
        self.assertContains(orders_page, 'customer1')

        status_response = self.client.post(reverse('admin_update_order_status', args=[order.id]), {
            'status': 'Delivered'
        })
        self.assertRedirects(status_response, reverse('admin_orders'))
        order.refresh_from_db()
        self.assertEqual(order.status, 'Delivered')

    def test_user_profile_update(self):
        self.client.login(username='customer1', password='customerpassword')
        profile_page = self.client.get(reverse('user_profile'))
        self.assertEqual(profile_page.status_code, 200)

        update_response = self.client.post(reverse('user_profile'), {
            'first_name': 'Shaamyak',
            'last_name': 'PS',
            'email': 'shaamyak@test.com',
            'phone': '9876543210',
            'address': 'MG Road, Bangalore'
        })
        self.assertEqual(update_response.status_code, 200)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Shaamyak')
        profile = UserProfile.objects.get(user=self.normal_user)
        self.assertEqual(profile.phone, '9876543210')
