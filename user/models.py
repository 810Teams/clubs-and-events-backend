from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from email_validator import validate_email, EmailNotValidError

from clubs_and_events.settings import STORAGE_BASE_DIR
from crum import get_current_user


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

    # Personal Information
    username = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to=get_profile_picture_path)
    cover_photo = models.ImageField(null=True, blank=True, upload_to=get_cover_photo_path)
    birthdate = models.DateField(null=True, blank=True)

    # Statuses
    is_lecturer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='user_created_by')
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='user_updated_by')

    # Others
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.pk is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(User, self).save(*args, **kwargs)


class EmailPreference(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    receive_request = models.BooleanField(default=True)
    receive_announcement = models.BooleanField(default=True)
    receive_community_event = models.BooleanField(default=True)
    receive_event = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.user.username)


class StudentCommitteeAuthority(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='student_committee_authority_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='student_committee_authority_updated_by')

    def __str__(self):
        return '{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.pk is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(StudentCommitteeAuthority, self).save(*args, **kwargs)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)
