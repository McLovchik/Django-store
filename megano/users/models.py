from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager

from application_settings.utils import check_image_size


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email: str, password: str, **extra_fields) -> 'User':
        """
        Create and save new user with email and password
        """
        if not email:
            raise ValueError('Email must be entering')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str) -> 'User':
        """
        Create superuser method
        """
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model
    """
    email = models.EmailField(verbose_name='email', unique=True)
    username = models.CharField(verbose_name='username', max_length=32, blank=True, null=True, default="")
    fullname = models.CharField(verbose_name='fullname', max_length=128, blank=True, null=True, default="")
    phone = models.CharField(verbose_name='phone number', max_length=16, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    is_staff = models.BooleanField(verbose_name='is_staff', default=False)
    is_active = models.BooleanField(verbose_name='is_active', default=True)
    is_superuser = models.BooleanField(verbose_name='is_superuser', default=False)
    avatar = models.ImageField(verbose_name='avatar', upload_to='avatars/', null=True, blank=True)
    city = models.CharField(verbose_name='city', max_length=32, null=True, blank=True, default="")
    address = models.CharField(verbose_name='address', max_length=128, null=True, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        if self.username:
            return str(self.username)
        else:
            return str(self.email)

    def save(self, *args, **kwargs) -> None:
        check_image_size(self.avatar)
        super(User, self).save(*args, **kwargs)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'profiles'
