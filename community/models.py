'''
    Community Application Models
    community/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import gettext as _

from category.models import ClubType, EventType, EventSeries
from clubs_and_events.settings import STORAGE_BASE_DIR, MAX_COMMUNITY_LOGO_DIMENSION, MAX_COMMUNITY_BANNER_DIMENSION
from core.utils.general import get_file_extension
from core.utils.files import auto_downscale_image
from core.utils.objects import save_user_attributes


class Community(models.Model):
    ''' Community model '''
    def get_logo_path(self, file_name):
        ''' Get logo path '''
        return '{}/community/{}/logo.{}'.format(STORAGE_BASE_DIR, self.id, get_file_extension(file_name))

    def get_banner_path(self, file_name):
        ''' Get banner path '''
        return '{}/community/{}/banner.{}'.format(STORAGE_BASE_DIR, self.id, get_file_extension(file_name))

    # Required Information
    name_th = models.CharField(max_length=128, unique=True)
    name_en = models.CharField(max_length=128, unique=True)

    # General Information
    url_id = models.CharField(max_length=32, null=True, blank=True, unique=True, default=None)
    description = models.TextField(max_length=1024, null=True, blank=True)
    external_links = models.TextField(max_length=512, null=True, blank=True)
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
        ''' String representation '''
        return '{}'.format(self.name_en)

    def clean(self, get_error=False):
        ''' Validate instance on save '''
        errors = list()

        if self.external_links is not None:
            urls = [i.replace('\r', '') for i in self.external_links.split('\n') if i.strip() != '']
            validate = URLValidator()

            for i in urls:
                try:
                    validate(i)
                except ValidationError:
                    errors.append(ValidationError(
                        _('External links contains an invalid URL. Each URL must be written on a new line.'),
                        code='invalid_url'
                    ))

        if get_error:
            return errors

        if len(errors) > 0:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')

        if self.pk is None:
            saved_logo, saved_banner = self.logo, self.banner
            self.logo, self.banner = None, None
            super(Community, self).save(*args, **kwargs)
            self.logo, self.banner = saved_logo, saved_banner

            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(Community, self).save(*args, **kwargs)

        auto_downscale_image(self.logo, threshold=MAX_COMMUNITY_LOGO_DIMENSION)
        auto_downscale_image(self.banner, threshold=MAX_COMMUNITY_BANNER_DIMENSION)


class Club(Community):
    ''' Club model '''
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

    def clean(self, get_error=False):
        ''' Validate instance on save '''
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

        if get_error:
            return errors

        if len(errors) > 0:
            raise ValidationError(errors)


class Event(Community):
    ''' Event model '''
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_approved = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    def clean(self, get_error=False):
        ''' Validate instance on save '''
        errors = super(Event, self).clean(get_error=True)

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if get_error:
            return errors

        if len(errors) > 0:
            raise ValidationError(errors)


class CommunityEvent(Event):
    ''' Community event model '''
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)

    def clean(self, get_error=False):
        ''' Validate instance on save '''
        errors = super(CommunityEvent, self).clean(get_error=True)

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
            errors.append(ValidationError(_('Community events are not able to be unapproved.'), code='status_error'))

        if get_error:
            return errors

        if len(errors) > 0:
            raise ValidationError(errors)


class Lab(Community):
    ''' Lab model '''
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    room = models.CharField(max_length=32, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='R')

    def clean(self, get_error=False):
        ''' Validate instance on save '''
        errors = super(Lab, self).clean(get_error=True)

        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-., '

        if self.tags is not None and self.tags.strip() != '':
            for i in self.tags:
                if i not in characters:
                    errors.append(ValidationError(
                        _('Tags must only consist of alphabetical characters, numbers, dashes, dots, and spaces. ' +
                          'Each tag are separated by commas.'),
                        code='invalid_tags'
                    ))

        if get_error:
            return errors

        if len(errors) > 0:
            raise ValidationError(errors)
