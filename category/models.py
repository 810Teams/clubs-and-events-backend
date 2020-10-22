'''
    Category Application Models
    category/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.db import models


class ClubType(models.Model):
    ''' Club type model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        ''' String representation '''
        return self.title_en


class EventType(models.Model):
    ''' Event type model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        ''' String representation '''
        return self.title_en


class EventSeries(models.Model):
    ''' Event series model '''
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        ''' String representation '''
        return self.title_en
