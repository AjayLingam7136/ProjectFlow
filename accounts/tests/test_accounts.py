from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAccountTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)

    def test_get_initials(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com',
            first_name='John', last_name='Doe', password='testpass123'
        )
        self.assertEqual(user.get_initials, 'JD')

    def test_get_initials_no_name(self):
        user = User.objects.create_user(
            username='abc', email='test@example.com', password='testpass123'
        )
        self.assertEqual(user.get_initials, 'AB')


class AuthViewTest(TestCase):
    def test_signup_view(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post(reverse('accounts:signup'), {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_to_dashboard(self):
        User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_when_logged_in(self):
        user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
