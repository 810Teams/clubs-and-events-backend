from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from category.models import ClubType, EventType, EventSeries
from clubs_and_events.settings import STORAGE_BASE_DIR
from crum import get_current_user


class Community(models.Model):
    def get_logo_path(self, file_name):
        file_extension = file_name.split('.')[1]
        return '{}/community/{}/logo.{}'.format(STORAGE_BASE_DIR, self.id, file_extension)

    def get_banner_path(self, file_name):
        file_extension = file_name.split('.')[1]
        return '{}/community/{}/banner.{}'.format(STORAGE_BASE_DIR, self.id, file_extension)

    # Required Information
    name_th = models.CharField(max_length=128, unique=True)
    name_en = models.CharField(max_length=128, unique=True)

    # General Information
    url_id = models.CharField(max_length=32, null=True, blank=True, unique=True, default=None)
    description = models.TextField(null=True, blank=True)
    external_links = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=get_logo_path)
    banner = models.ImageField(null=True, blank=True, upload_to=get_banner_path)

    # Settings
    is_publicly_visible = models.BooleanField(default=False)
    is_accepting_requests = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='community_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='community_updated_by')

    def __str__(self):
        return '{}'.format(self.name_en)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Community, self).save(*args, **kwargs)


class Club(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    club_type = models.ForeignKey(ClubType, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.CharField(max_length=32, null=True, blank=True, default=None)
    founded_date = models.DateField(null=True, blank=True)
    is_official = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS, default='R')
    valid_through = models.DateField(null=True, blank=True)

    def clean(self):
        errors = list()

        if not self.is_official:
            if self.room != None:
                errors.append(ValidationError(
                    _('Unofficial clubs are not able to occupy a room.'),
                    code='unofficial_club_limitations'
                ))
            if self.url_id != None:
                errors.append(ValidationError(
                    _('Unofficial clubs are not able to set custom URL ID.'),
                    code='unofficial_club_limitations'
                ))
            if self.is_publicly_visible:
                errors.append(ValidationError(
                    _('Unofficial clubs cannot be publicly visible.'),
                    code='unofficial_club_limitations'
                ))
            if self.valid_through is not None:
                errors.append(ValidationError(
                    _('Unofficial clubs must not have a valid through date.'),
                    code='not_null_valid_through_date'
                ))


        elif self.is_official and self.valid_through is None:
            errors.append(ValidationError(
                _('Official clubs must have a valid through date.'),
                code='null_valid_through_date'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class Event(Community):
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_approved = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)


class CommunityEvent(Event):
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)

    def clean(self):
        errors = list()

        try:
            if Event.objects.get(pk=self.created_under.id) is not None:
                errors.append(ValidationError(
                    _('Community events are not able to be created under events.'),
                    code='hierarchy_error'
                ))
        except Event.DoesNotExist:
            pass

        try:
            if not Club.objects.get(pk=self.created_under.id).is_official:
                errors.append(ValidationError(
                    _('Community events are not able to be created under unofficial clubs.'),
                    code='unofficial_club_limitations'
                ))
        except Club.DoesNotExist:
            pass

        if not self.is_approved:
            errors.append(ValidationError(
                _('Community events are not able to be unapproved.'),
                code='status_error'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class Lab(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    room = models.CharField(max_length=32, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='R')
