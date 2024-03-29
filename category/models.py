'''
    Category Application Models
    category/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.db import models

from core.utils.objects import save_user_attributes


class ClubType(models.Model):
    ''' Club type model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='club_type_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='club_type_updated_by')

    def __str__(self):
        ''' String representation '''
        return self.title_en

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(ClubType, self).save(*args, **kwargs)


class EventType(models.Model):
    ''' Event type model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='event_type_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='event_type_updated_by')

    def __str__(self):
        ''' String representation '''
        return self.title_en

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(EventType, self).save(*args, **kwargs)


class EventSeries(models.Model):
    ''' Event series model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='event_series_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='event_series_updated_by')

    def __str__(self):
        ''' String representation '''
        return self.title_en

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')
        super(EventSeries, self).save(*args, **kwargs)
