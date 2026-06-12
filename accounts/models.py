from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ('client', 'Client'),
        ('admin',  'Administrateur'),
    ]
    email = models.EmailField(unique=True)
    tel   = models.CharField(max_length=20, blank=True)
    role  = models.CharField(max_length=10, choices=ROLES, default='client')

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_staff
