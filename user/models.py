from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **kwargs):
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    def get_profile_picture_path(self, file_name):
        file_extension = file_name.split('.')[1]
        return '{}/user/{}/profile_picture.{}'.format(STORAGE_BASE_DIR, self.username, file_extension)

    def get_cover_photo_path(self, file_name):
        file_extension = file_name.split('.')[1]
        return '{}/user/{}/cover_photo.{}'.format(STORAGE_BASE_DIR, self.username, file_extension)

    username = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True, null=True, blank=True)

    nickname = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to=get_profile_picture_path)
    cover_photo = models.ImageField(null=True, blank=True, upload_to=get_cover_photo_path)
    birthdate = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return '{}'.format(self.username)


class EmailPreference(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    receive_own_club = models.BooleanField(default=True)
    receive_own_event = models.BooleanField(default=True)
    receive_own_lab = models.BooleanField(default=True)
    receive_other_events = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.user.username)


class StudentCommitteeAuthority(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '{}'.format(self.user.username)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)
