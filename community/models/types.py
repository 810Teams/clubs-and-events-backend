from django.db import models

class ClubType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

class EventType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

class EventSeries(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)
