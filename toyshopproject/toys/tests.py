from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Toy

class ToyShopInventoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Toy Shop Inventory System')
        self.assertContains(response, '2026')
        self.assertContains(response, 'Add Toy')
        self.assertContains(response, 'View Toys')

    def test_login_protection(self):
        response = self.client.get(reverse('toy_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

        response = self.client.get(reverse('add_toy'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_login_and_logout(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('toy_list'))

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_add_and_view_toy(self):
        self.client.login(username='testuser', password='password123')

        response = self.client.post(reverse('add_toy'), {
            'toy_name': 'Lego City Police',
            'age_group': '5-8 Years',
            'category': 'Building Blocks',
            'price': '1299'
        })
        self.assertRedirects(response, reverse('toy_list'))

        self.assertEqual(Toy.objects.count(), 1)
        toy = Toy.objects.first()
        self.assertEqual(toy.toy_name, 'Lego City Police')

        response = self.client.get(reverse('toy_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lego City Police')
        self.assertContains(response, 'Welcome, testuser')

    def test_edit_toy(self):
        self.client.login(username='testuser', password='password123')
        toy = Toy.objects.create(
            toy_name='Rubik Cube',
            age_group='7+ Years',
            category='Puzzle',
            price='250'
        )

        response = self.client.post(reverse('edit_toy', args=[toy.id]), {
            'toy_name': 'Rubiks Speed Cube 3x3',
            'age_group': '8+ Years',
            'category': 'Brain Games',
            'price': '350'
        })
        self.assertRedirects(response, reverse('toy_list'))

        toy.refresh_from_db()
        self.assertEqual(toy.toy_name, 'Rubiks Speed Cube 3x3')
        self.assertEqual(toy.price, '350')

    def test_delete_toy(self):
        self.client.login(username='testuser', password='password123')
        toy = Toy.objects.create(
            toy_name='Toy Car',
            age_group='3-5 Years',
            category='Vehicles',
            price='150'
        )
        self.assertEqual(Toy.objects.count(), 1)

        response = self.client.get(reverse('delete_toy', args=[toy.id]))
        self.assertRedirects(response, reverse('toy_list'))
        self.assertEqual(Toy.objects.count(), 0)
