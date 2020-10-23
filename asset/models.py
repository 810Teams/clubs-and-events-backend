'''
    Asset Application Models
    asset/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Community, Event, CommunityEvent
from core.utils import truncate, get_client_ip
from crum import get_current_request, get_current_user


class Announcement(models.Model):
    ''' Announcement model '''
    def get_image_path(self, file_name):
        ''' Retrieve image path '''
        return '{}/announcement/{}/{}'.format(STORAGE_BASE_DIR, self.id, file_name)

    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    is_publicly_visible = models.BooleanField(default=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_updated_by')

    def __str__(self):
        ''' String representation '''
        return '"{}", {}'.format(truncate(self.text, max_length=32), self.community.name_en)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(Announcement, self).save(*args, **kwargs)
            self.image = saved_image

            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(Announcement, self).save(*args, **kwargs)


class Album(models.Model):
    ''' Album model '''
    name = models.CharField(max_length=128)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='album_created_in')
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='album_linked_to')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_updated_by')

    def __str__(self):
        ''' String representation '''
        return self.name

    def save(self, *args, **kwargs):
        ''' Save instance '''
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Album, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate instance on save '''
        errors = list()

        try:
            if CommunityEvent.objects.get(pk=self.community.id):
                errors.append(ValidationError(
                    _('Albums are not able to be created under community events.'),
                    code='hierarchy_error'
                ))
        except CommunityEvent.DoesNotExist:
            pass

        try:
            if Event.objects.get(pk=self.community.id) is not None and self.community_event is not None:
                errors.append(ValidationError(
                    _('Albums are not able to be linked to community events if created under an event.'),
                    code='hierarchy_error'
                ))
        except Event.DoesNotExist:
            pass

        if self.community_event is not None and (self.community.id != self.community_event.created_under.id):
            errors.append(ValidationError(
                _('Albums are not able to be linked to community events created under other communities.'),
                code='hierarchy_error'
            ))

        if len(errors) > 0:
            raise ValidationError(errors)


class AlbumImage(models.Model):
    ''' Album image model '''
    def get_image_path(self, file_name):
        ''' Retrieve image path '''
        return '{}/album/{}/{}'.format(STORAGE_BASE_DIR, self.album.id, file_name)

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_image_created_by')

    def __str__(self):
        ''' String representation '''
        return '{} ({})'.format(self.album.__str__(), self.id)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user

        super(AlbumImage, self).save(*args, **kwargs)


class Comment(models.Model):
    ''' Comment model '''
    text = models.TextField()
    written_by = models.CharField(max_length=64)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.CharField(max_length=15)

    def __str__(self):
        ''' String representation '''
        return '"{}", {}, {}'.format(truncate(self.text, max_length=32), self.written_by, self.event.__str__())

    def save(self, *args, **kwargs):
        ''' Save instance '''
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.ip_address = get_client_ip(get_current_request())

        super(Comment, self).save(*args, **kwargs)
