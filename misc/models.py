'''
    Miscellaneous Application Models
    misc/models.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import STORAGE_BASE_DIR
from community.models import Event
from core.utils.general import truncate, get_file_extension, has_instance
from core.utils.objects import save_user_attributes
from membership.models import Membership


class FAQ(models.Model):
    ''' Frequently asked question (FAQ) model '''
    def get_image_path(self, file_name):
        ''' Retrieve image path '''
        return '{}/faq/{}.{}'.format(STORAGE_BASE_DIR, self.id, get_file_extension(file_name))

    question = models.CharField(max_length=255)
    question_th = models.CharField(max_length=255)
    answer = models.TextField(max_length=2048)
    answer_th = models.TextField(max_length=2048)
    image = models.ImageField(null=True, blank=True, upload_to=get_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='faq_created_by')
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='faq_updated_by')

    def __str__(self):
        ''' String representation '''
        return '{}'.format(truncate(self.question, max_length=32))

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='created_by', updated_by_field_name='updated_by')

        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(FAQ, self).save(*args, **kwargs)
            self.image = saved_image

            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(FAQ, self).save(*args, **kwargs)


class Vote(models.Model):
    ''' Vote model '''
    comment = models.TextField(max_length=512, blank=True)
    voted_for = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='vote_voted_for')
    voted_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='vote_voted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        ''' Save instance '''
        save_user_attributes(self, created_by_field_name='voted_by', updated_by_field_name=None)
        super(Vote, self).save(*args, **kwargs)

    def clean(self):
        ''' Validate on save '''
        errors = list()

        if not has_instance(self.voted_for.community, Event):
            errors.append(ValidationError(_('Votes can only be casted in events.'), code='non_event'))

        if len(errors) > 0:
            raise ValidationError(errors)
