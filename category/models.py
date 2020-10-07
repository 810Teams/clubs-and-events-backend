from django.db import models


class ClubType(models.Model):
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_en


class EventType(models.Model):
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_en


class EventSeries(models.Model):
    title_th = models.CharField(max_length=64)
    title_en = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_en
