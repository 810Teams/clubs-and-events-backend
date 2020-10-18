import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage

from membership.models import MembershipLog


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=255):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def truncate(text, max_length=64):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def filter_queryset(queryset, request, target_param=None, is_foreign_key=False):
    try:
        query = request.query_params.get(target_param)
        if query is not None:
            queryset = eval('queryset.filter({}{}=query)'.format(target_param, '_id' * is_foreign_key))
    except (ValueError, ValidationError):
        queryset = None

    return queryset


def limit_queryset(queryset, request, target_param='limit'):
    try:
        limit = request.query_params.get(target_param)
        if limit is not None:
            queryset = queryset[:min(int(limit), len(queryset))]
    except ValueError:
        pass

    return queryset


def get_previous_membership_log(obj):
    if not isinstance(obj, MembershipLog):
        return None

    logs = MembershipLog.objects.filter(membership_id=obj.membership.id)

    current = 0
    for i in range(len(logs)):
        if logs[i].id == obj.id:
            current = i
            break

    if current == 0:
        return None
    return logs[current - 1]


def get_email(user, domain_name='it.kmitl.ac.th'):
    return user.username + '@' + domain_name


def filter_queryset_permission(queryset, request, permissions):
    for i in permissions:
        visible_ids = [j.id for j in queryset if i.has_permission(request, None)]
        queryset = queryset.filter(pk__in=visible_ids)
        visible_ids = [j.id for j in queryset if i.has_object_permission(request, None, j)]
        queryset = queryset.filter(pk__in=visible_ids)
    return queryset
