from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Community, CommunityEvent, Event
from core.utils import truncate
from crum import get_current_user


class Announcement(models.Model):
    def get_image_path(self, file_name):
        return '{}/announcement/{}/{}'.format(STORAGE_BASE_DIR, self.id, file_name)

    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_updated_by')

    def __str__(self):
        return '"{}" - {}'.format(truncate(self.text, max_length=32), self.community.name_en)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Announcement, self).save(*args, **kwargs)


class Album(models.Model):
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
        return self.name

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user
        self.updated_by = user

        super(Album, self).save(*args, **kwargs)

    def clean(self):
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
    def get_image_path(self, file_name):
        return '{}/album/{}/{}'.format(STORAGE_BASE_DIR, self.album.id, file_name)

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_image_created_by')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user

        super(AlbumImage, self).save(*args, **kwargs)


class Comment(models.Model):
    text = models.TextField()
    written_by = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '"{}" - {}'.format(truncate(self.text, max_length=32), self.written_by)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None and user.id is None:
            user = None
        if self.id is None:
            self.created_by = user

        super(Comment, self).save(*args, **kwargs)
