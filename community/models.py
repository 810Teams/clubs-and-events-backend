from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from category.models import ClubType, EventType, EventSeries


class Community(models.Model):
    name_th = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=64, unique=True)
    url_id = models.CharField(max_length=16, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    is_publicly_visible = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.name_en)


class Club(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    club_type = models.ForeignKey(ClubType, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.CharField(max_length=32, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    is_official = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS, default='R')

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

        if len(errors) > 0:
            raise ValidationError(errors)


class Event(Community):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('C', 'Cancelled'),
    )

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=1, choices=STATUS, default='W')

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)


class CommunityEvent(Event):
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._meta.get_field('status').default = 'A'

    def clean(self):
        errors = list()

        if self.id == self.created_under.id:
            errors.append(ValidationError(
                _('Community events are not able to be created under its parent self.'),
                code='hierarchy_error'
            ))

        try:
            if Event.objects.get(pk=self.created_under.id) != None:
                errors.append(ValidationError(
                    _('Community events are not able to be created under events.'),
                    code='hierarchy_error'
                ))
        except Event.DoesNotExist:
            pass

        try:
            if Club.objects.get(pk=self.created_under.id) and not Club.objects.get(pk=self.created_under.id).is_official:
                errors.append(ValidationError(
                    _('Community events are not able to be created under unofficial clubs.'),
                    code='unofficial_club_limitations'
                ))
        except Club.DoesNotExist:
            pass

        if self.status == 'W':
            errors.append(ValidationError(
                _('Community events are not able to have waiting as status.'),
                code='status_error'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)

    def __str__(self):
        return '{}\'s {}'.format(self.created_under.name_en, self.name_en)


class Lab(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    room = models.CharField(max_length=16, null=True, blank=True)
    founded_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='R')
