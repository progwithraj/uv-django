from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('dept', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, username, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        return self.get(email=username)

# Create your models here.
class MyUser(AbstractBaseUser, PermissionsMixin):
    
    # custome dept choice
    DEPT_CHOICES = [
        ('DEV', 'Developer'),
        ('SALES', 'Sales'),
        ('MANAGER', 'Manager'),
        ('HR', 'Human Resource'),
        ('FINANCE', 'Finance'),
        ('MARKETING', 'Marketing'),
        ('ADMIN', 'Admin'),
    ]
    
    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
        error_messages={
            'unique': 'Email address already exists'
        }
    )
    username = models.CharField(verbose_name=_('user name'), max_length=255, unique=True, error_messages={
            'unique': 'Username already exists'
        })
    # EXTRA FIELDS
    phone = models.CharField(max_length=15, null=True, blank=True)
    dept = models.CharField(max_length=10, choices=DEPT_CHOICES, null=True, blank=True, default='DEV')
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyUserManager()
    def __str__(self):
        return self.username
