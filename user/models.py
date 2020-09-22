from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=32, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True)
    cover_photo = models.ImageField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    last_online = models.DateTimeField(null=True, blank=True)
    is_lecturer = models.BooleanField()

    def __str__(self):
        return '{}'.format(self.user.username)


class EmailPreference(models.Model):
    receive_own_club = models.BooleanField(default=True)
    receive_own_event = models.BooleanField(default=True)
    receive_own_lab = models.BooleanField(default=True)
    receive_other_events = models.BooleanField(default=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.profile.user.username)


class StudentCommitteeAuthority(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '{}'.format(self.profile.user.username)

    def clean(self):
        errors = list()

        if self.start_date > self.end_date:
            errors.append(ValidationError(_('Start date must come before the end date.'), code='date_period_error'))

        if len(errors) > 0:
            raise ValidationError(errors)
