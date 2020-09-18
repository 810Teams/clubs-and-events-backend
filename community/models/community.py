from django.db import models
from community.models.types import ClubType
from community.models.types import EventType
from community.models.types import EventSeries

class Community(models.Model):
    name_th = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    url_id = models.CharField(max_length=16, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    is_publicly_visible = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def update_community(self, url_id, description, logo, banner, is_publicly_visible):
        self.url_id = url_id
        self.description = description
        self.logo = logo
        self.banner = banner
        self.is_publicly_visible = is_publicly_visible

class Club(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    club_type = models.ForeignKey(ClubType, on_delete=models.SET_NULL, null=True)
    room = models.CharField(max_length=16, null=True, blank=True)
    founded_date = models.DateField()
    is_official = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS, default='R')

    def update_club(self, url_id, description, logo, banner, is_publicly_visible, club_type, room, founded_date,
                    status):
        super().update_community(url_id, description, logo, banner, is_publicly_visible)
        self.club_type = club_type
        self.room = room
        self.founded_date = founded_date
        self.status = status

class Event(Community):
    STATUS = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('C', 'Cancelled'),
    )

    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True)
    event_series = models.ForeignKey(EventSeries, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(choices=STATUS, default='W')

    def update_event(self, url_id, description, logo, banner, is_publicly_visible, event_type, event_series, location,
                     start_date, end_date, start_time, end_time, status):
        super().update_community(url_id, description, logo, banner, is_publicly_visible)
        self.event_type = event_type
        self.event_series = event_series
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.status = status

class CommunityEvent(Event):
    created_under = models.ForeignKey(Community, on_delete=models.PROTECT)
    allows_outside_participators = models.BooleanField(default=False)

    def update_community_event(self, url_id, description, logo, banner, is_publicly_visible, event_type, event_series,
                               location, start_date, end_date, start_time, end_time, status,
                               allows_outside_participators):
        super().update_event(url_id, description, logo, banner, is_publicly_visible, event_type, event_series, location,
                             start_date, end_date, start_time, end_time, status)
        self.allows_outside_participators = allows_outside_participators

class Lab(Community):
    STATUS = (
        ('R', 'Recruiting'),
        ('C', 'Closed'),
        ('D', 'Disbanded'),
    )

    room = models.CharField(max_length=16, null=True, blank=True)
    founded_date = models.DateField()
    tags = models.CharField(max_length=64)
    status = models.CharField(choices=STATUS, default='R')

    def update_lab(self, url_id, description, logo, banner, is_publicly_visible, room, founded_date, tags, status):
        super().update_community(url_id, description, logo, banner, is_publicly_visible)
        self.room = room
        self.founded_date = founded_date
        self.tags = tags
        self.status = status
