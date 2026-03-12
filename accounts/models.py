from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_END_USER = 'end_user'
    ROLE_AGENT = 'agent'
    ROLE_MANAGER = 'manager'

    ROLE_CHOICES = [
        (ROLE_END_USER, 'End User'),
        (ROLE_AGENT, 'IT Support Agent'),
        (ROLE_MANAGER, 'IT Manager / Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_END_USER)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_end_user(self):
        return self.role == self.ROLE_END_USER

    @property
    def is_agent(self):
        return self.role in [self.ROLE_AGENT, self.ROLE_MANAGER]

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    def get_avatar_url(self):
        """Return avatar URL or a placeholder image with initials."""
        if self.avatar:
            return self.avatar.url
        # Placeholder image using initials
        return f"https://via.placeholder.com/50?text={self.get_initials()}"

    def get_initials(self):
        """Return first letters of first and last name, or first 2 of username."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()