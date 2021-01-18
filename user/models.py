'''
    User Application Models
    user/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR, LDAP_USER_GROUPS
from clubs_and_events.settings import MAX_PROFILE_PICTURE_DIMENSION, MAX_COVER_PHOTO_DIMENSION
from core.utils.general import get_file_extension
from core.utils.files import auto_downscale_image
from core.utils.objects import save_user_attributes


class UserManager(BaseUserManager):
    ''' User manager '''
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
    ''' User model '''
    def get_profile_picture_path(self, file_name):
        ''' Get profile picture path '''
        return '{}/user/{}/profile_picture.{}'.format(STORAGE_BASE_DIR, self.username, get_file_extension(file_name))

    def get_cover_photo_path(self, file_name):
        ''' Get cover photo path '''
        return '{}/user/{}/cover_photo.{}'.format(STORAGE_BASE_DIR, self.username, get_file_extension(file_name))

    # Personal Information
    username = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(max_length=4096, null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to=get_profile_picture_path)
    birthdate = models.DateField(null=True, blank=True)

    # Statuses
    USER_GROUPS = tuple([(i['user_group'], i['display_name']) for i in LDAP_USER_GROUPS])

    user_group = models.CharField(max_length=8, choices=USER_GROUPS, default='student')
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
        ''' String representation '''
        return self.username

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(User, self).save(*args, **kwargs)
        auto_downscale_image(self.profile_picture, threshold=MAX_PROFILE_PICTURE_DIMENSION)


class EmailPreference(models.Model):
    ''' Email preference model '''
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    receive_request = models.BooleanField(default=True)
    receive_announcement = models.BooleanField(default=True)
    receive_community_event = models.BooleanField(default=True)
    receive_event = models.BooleanField(default=True)
    receive_invitation = models.BooleanField(default=True)

    def __str__(self):
        ''' String representation '''
        return '{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        self.user.save()
        super(EmailPreference, self).save(*args, **kwargs)


class StudentCommitteeAuthority(models.Model):
    ''' Student committee authority model '''
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='student_committee_authority_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='student_committee_authority_updated_by')

    def __str__(self):
        ''' String representation '''
        return '{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(StudentCommitteeAuthority, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate instance on save '''
        errors = list()

        if self.user.user_group != 'student':
            errors.append(ValidationError(
                _('Student committee authority can only be granted to students.'), code='student_committee_error'
            ))

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)
