from django.db import models


class ClubType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    class Meta:
        db_table = 'club_types'

    def __str__(self):
        return '{}'.format(self.title_en)


class EventType(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    class Meta:
        db_table = 'event_types'

    def __str__(self):
        return '{}'.format(self.title_en)


class EventSeries(models.Model):
    title_th = models.CharField(max_length=32)
    title_en = models.CharField(max_length=32)

    class Meta:
        db_table = 'event_series'

    def __str__(self):
        return '{}'.format(self.title_en)
