from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PasswordChangeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword123',
        )
        self.client = Client()

    def test_password_change_page_loads(self):
        self.client.login(email='test@example.com', password='testpassword123')
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Change Password')
        self.assertContains(response, 'Old password')
        self.assertContains(response, 'New password')
        # Verify styled form widgets
        self.assertContains(response, 'form-input')
        self.assertContains(response, 'form-label')
        self.assertContains(response, 'auth-card')
        self.assertContains(response, 'auth-form')

    def test_password_change_requires_login(self):
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_form_valid(self):
        self.client.login(email='test@example.com', password='testpassword123')
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'testpassword123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_password_change_wrong_old_password(self):
        self.client.login(email='test@example.com', password='testpassword123')
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'wrongpassword',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'was entered incorrectly')
