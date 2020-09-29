from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from community.models import Community, CommunityEvent, Event
from core.utils import truncate
from user.models import User


class Announcement(models.Model):
    def get_image_path(self, file_name):
        return 'storage/announcement/{}/{}'.format(self.id, file_name)

    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='announcement_updated_by')

    def __str__(self):
        return '"{}" - {}'.format(truncate(self.text, max_length=32), self.community.name_en)


class Album(models.Model):
    name = models.CharField(max_length=128)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='album_created_in')
    community_event = models.ForeignKey(CommunityEvent, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='album_linked_to')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_updated_by')

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

    def __str__(self):
        return '{}\'{} {}'.format(self.community, 's' * (self.community.name_en[-1] != 's'), self.name)


class AlbumImage(models.Model):
    def get_image_path(self, file_name):
        return 'storage/album/{}/{}'.format(self.album.id, file_name)

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='album_image_created_by')


class Comment(models.Model):
    text = models.TextField()
    written_by = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return '"{}" - {}'.format(truncate(self.text, max_length=32), self.written_by)
