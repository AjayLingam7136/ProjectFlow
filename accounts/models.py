from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model for future extensibility."""

    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('system', 'System'),
    ]

    email = models.EmailField('email address', unique=True)
    avatar = models.ImageField('avatar', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('bio', blank=True, max_length=500)
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def get_initials(self):
        """Return initials for avatar placeholder."""
        first = self.first_name[0] if self.first_name else ''
        last = self.last_name[0] if self.last_name else ''
        if first and last:
            return f"{first}{last}".upper()
        return (self.username[:2] if self.username else 'U').upper()
