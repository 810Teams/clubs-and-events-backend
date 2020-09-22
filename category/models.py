from django.db import models


class ClubType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)


class EventType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)


class EventSeries(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.title_en)
